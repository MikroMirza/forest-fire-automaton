mod experiments;

use minifb::{Key, Window, WindowOptions};
use std::thread;
use std::time::Duration;

use experiments::*;
use grid_lib::*;

const NUM_OF_THREADS: usize = 8;

fn run_viewer(parallel: bool) {
    let mut grid = Grid::new(512, 512);
    grid.set(100, 100, PixelState::Burning);

    let mut window = Window::new(
        "Forest Fire",
        512,
        512,
        WindowOptions::default(),
    ).unwrap();

    let mut buffer = vec![0u32; 512 * 512];

    while window.is_open() && !window.is_key_down(Key::Escape) {

        if parallel {
            grid.step_parallel(NUM_OF_THREADS);
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

        window.update_with_buffer(&buffer, 512, 512).unwrap();
        thread::sleep(Duration::from_millis(0));
    }
}


fn run_benchmarks() {
    let base_grid_size = 256;
    let steps = 10;

    let strong = strong_scaling_rust(&Grid::new(base_grid_size, base_grid_size), steps);

    let weak = weak_scaling_rust(base_grid_size, steps);

    println!("Strong scaling:");
    for (w, s) in &strong { println!("Workers: {:2} | Speedup: {:.3}", w, s); }

    println!("Weak scaling:");
    for (w, e) in &weak { println!("Workers: {:2} | Efficiency: {:.3}", w, e); }
    plot_scaling(&strong, &weak).unwrap();
}



fn main() {
    let args: Vec<String> = std::env::args().collect();

    match args.get(1).map(|s| s.as_str()) {

        Some("bench") => {
            run_benchmarks();
        }

        Some("parallel") => {
            run_viewer(true);
        }

        _ => {
            run_viewer(false);
        }
    }
}
