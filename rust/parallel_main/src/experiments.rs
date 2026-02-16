use std::time::Instant;
use grid_lib::Grid;

pub fn measure_time(grid: &Grid, steps: usize, workers: usize) -> f64 {
    let mut times = vec![];

    for _ in 0..5 {
        let mut g = grid.clone();

        let start = Instant::now();

        for _ in 0..steps {
            if workers == 0 {
                g.step_sequential();
            } else {
                g.step_parallel(workers);
            }
        }

        times.push(start.elapsed().as_secs_f64());
    }

    times.iter().sum::<f64>() / times.len() as f64
}
pub fn strong_scaling_rust(grid: &Grid, steps: usize) -> Vec<(usize, f64)> {
    let seq_time = measure_time(grid, steps, 0);
    let max_workers = num_cpus::get();

    let mut results = vec![];

    for workers in 1..=max_workers {
        let par_time = measure_time(grid, steps, workers);
        let speedup = seq_time / par_time;

        results.push((workers, speedup));
    }

    results
}

pub fn weak_scaling_rust(base_grid_size: usize, steps: usize) -> Vec<(usize, f64)> {
    let max_workers = num_cpus::get();
    let mut results = vec![];

    for workers in 1..=max_workers {
        let scaled_rows = base_grid_size * workers;
        let scaled_cols = base_grid_size;

        let grid = Grid::new(scaled_rows, scaled_cols);
        let time = measure_time(&grid, steps, workers);

        let efficiency = time / measure_time(&Grid::new(base_grid_size, base_grid_size), steps, 1.0 as usize);

        results.push((workers, efficiency));
    }

    results
}

use plotters::prelude::*;

pub fn plot_scaling(strong: &[(usize, f64)], weak: &[(usize, f64)]) -> Result<(), Box<dyn std::error::Error>> {
    let root = BitMapBackend::new("scaling.png", (1024, 768)).into_drawing_area();
    root.fill(&WHITE)?;

    let max_workers = strong.iter().map(|(w, _)| *w).max().unwrap_or(1);
    let max_speedup = strong.iter().map(|(_, s)| *s).fold(0./0., f64::max).max(weak.iter().map(|(_, e)| *e).fold(0./0., f64::max));

    let mut chart = ChartBuilder::on(&root)
        .caption("Strong vs Weak", ("sans-serif", 40))
        .margin(20)
        .x_label_area_size(40)
        .y_label_area_size(60)
        .build_cartesian_2d(0..max_workers, 0.0..max_speedup)?;

    chart.configure_mesh()
        .x_desc("Workers")
        .y_desc("Speedup / Efficiency")
        .draw()?;
    chart.draw_series(LineSeries::new(
        strong.iter().map(|(w, s)| (*w, *s)),
        &RED,
    ))?.label("Strong Scaling").legend(|(x, y)| PathElement::new([(x, y), (x+20, y)], &RED));
    chart.draw_series(LineSeries::new(
        weak.iter().map(|(w, e)| (*w, *e)),
        &BLUE,
    ))?.label("Weak Scaling").legend(|(x, y)| PathElement::new([(x, y), (x+20, y)], &BLUE));

    chart.configure_series_labels().background_style(&WHITE.mix(0.8)).border_style(&BLACK).draw()?;

    Ok(())
}
