mod experiments;

use minifb::{Key, Window, WindowOptions};
use std::thread;
use std::time::Duration;

use experiments::*;
use grid_lib::*;

// const NUM_OF_THREADS: usize = 8;

fn run_viewer(parallel: bool) {
    let mut grid = Grid::new(2048, 2048);
    grid.set(100, 100, PixelState::Burning);

    let mut window = Window::new(
        "Forest Fire",
        2048,
        2048,
        WindowOptions::default(),
    ).unwrap();

    let mut buffer = vec![0u32; 2048* 2048];
    let threads = num_cpus::get();

    while window.is_open() && !window.is_key_down(Key::Escape) {

        if parallel {
            grid.step_parallel(threads);
        } else {
            grid.step_sequential();
        }

        for row in 0..grid.rows {
            for col in 0..grid.cols {
                let (r, g, b) = grid.color_of(grid.get(row, col));
                let idx = row * grid.cols + col;

                buffer[idx] =
                    ((r as u32) << 16) |
                    ((g as u32) << 8) |
                    (b as u32);
            }
        }

        window.update_with_buffer(&buffer, 2048, 2048).unwrap();
        thread::sleep(Duration::from_millis(0));
    }
}


fn run_benchmarks() {
    let base_grid_size = 2048;
    let steps = 300;

    let grid = Grid::new(base_grid_size, base_grid_size);

    let raw = strong_scaling_raw_table(&grid, steps);
    let raw_weak = weak_scaling_raw_table(base_grid_size, steps);

    print_weak_raw_table(&raw_weak);
    print_raw_table(&raw);

    let sp_rows = compute_sp(&raw);
    let (mean_s, std_s, mean_p, std_p) = sp_stats(&sp_rows);

    println!("\n=== Sequential / Parallel Fractions (4 threads) ===");
    println!("S: mean = {:.3}, std_dev = {:.3}", mean_s, std_s);
    println!("P: mean = {:.3}, std_dev = {:.3}", mean_p, std_p);
}


fn main() -> Result<(), Box<dyn std::error::Error>> {
    let base_grid_size = 512;
    let steps = 200;

    let grid = Grid::new(base_grid_size, base_grid_size);

    let raw_strong = strong_scaling_raw_table(&grid, steps);
    print_raw_table(&raw_strong);

    let sp_rows = compute_sp(&raw_strong);
    let (mean_s, std_s, mean_p, std_p) = sp_stats(&sp_rows);

    println!("\n=== Sequential / Parallel Fractions (4 threads) ===");
    println!("S: mean = {:.3}, std_dev = {:.3}", mean_s, std_s);
    println!("P: mean = {:.3}, std_dev = {:.3}", mean_p, std_p);

    let strong_results: Vec<ResultRow> = raw_strong.iter().map(|(workers, times)| {
        let m = times.iter().sum::<f64>() / times.len() as f64;
        ResultRow {
            workers: *workers,
            mean: if *workers == 0 { 1.0 } else { raw_strong[1].1.iter().sum::<f64>() / times.len() as f64 / m }, 
            std_dev: std_dev(times, m),
            outlier: outlier(times, m),
        }
    }).collect();

    plot_strong(&strong_results)?;

    // --- Weak Scaling ---
    let raw_weak = weak_scaling_raw_table(base_grid_size, steps);
    print_weak_raw_table(&raw_weak);

    let weak_results: Vec<ResultRow> = raw_weak.iter().map(|(workers, times)| {
        let m = times.iter().sum::<f64>() / times.len() as f64;
        ResultRow {
            workers: *workers,
            mean: raw_weak[0].1.iter().sum::<f64>() / times.len() as f64 / m, // efficiency relative to 1T
            std_dev: std_dev(times, m),
            outlier: outlier(times, m),
        }
    }).collect();

    plot_weak(&weak_results)?;

    println!("\n=== Plots generated: strong_scaling.png, weak_scaling.png ===");

    Ok(())
}

