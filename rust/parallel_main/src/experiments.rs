use std::time::Instant;
use grid_lib::Grid;
use plotters::prelude::*;
use rand::Rng;

pub struct ResultRow {
    pub workers: usize,
    pub mean: f64,
    pub std_dev: f64,
    pub outlier: f64,
}

pub struct SpRow {
    pub workers: usize,
    pub s: f64,
    pub p: f64,
}
pub fn compute_sp(raw_data: &[(usize, Vec<f64>)]) -> Vec<SpRow> {
    let mut sp_rows = Vec::new();

    let serial_times = &raw_data[0].1;
    let t4_times = raw_data.iter()
        .find(|(workers, _)| *workers == 4)
        .map(|(_, times)| times)
        .expect("No 4-thread data found");

    for i in 0..serial_times.len() {
        let t1 = serial_times[i];
        let t4 = t4_times[i];

        let s = ((t4 / t1) * 4.0 - 1.0) / 3.0;
        let s = s.clamp(0.0, 1.0);
        let p = 1.0 - s;

        sp_rows.push(SpRow {
            workers: 4,
            s,
            p,
        });
    }

    sp_rows
}

pub fn sp_stats(sp_rows: &[SpRow]) -> (f64, f64, f64, f64) {
    let s_values: Vec<f64> = sp_rows.iter().map(|r| r.s).collect();
    let p_values: Vec<f64> = sp_rows.iter().map(|r| r.p).collect();

    let mean_s = mean(&s_values);
    let std_s = std_dev(&s_values, mean_s);

    let mean_p = mean(&p_values);
    let std_p = std_dev(&p_values, mean_p);

    (mean_s, std_s, mean_p, std_p)
}


pub fn mean(data: &[f64]) -> f64 {
    data.iter().sum::<f64>() / data.len() as f64
}

pub fn std_dev(data: &[f64], mean: f64) -> f64 {
    let variance = data.iter()
        .map(|v| (v - mean).powi(2))
        .sum::<f64>() / data.len() as f64;

    variance.sqrt()
}

pub fn outlier(data: &[f64], mean: f64) -> f64 {
    data.iter()
        .cloned()
        .max_by(|a, b| (a - mean).abs().partial_cmp(&(b - mean).abs()).unwrap())
        .unwrap_or(0.0)
}

pub fn measure_time(grid: &Grid, steps: usize, workers: usize) -> Vec<f64> {
    let mut times = vec![];

    for _ in 0..30 {
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

    times
}


pub fn strong_scaling_rust(
    grid: &Grid,
    steps: usize
) -> Vec<ResultRow> {

    let max_workers = num_cpus::get();
    let mut results = vec![];

    let base_runs = measure_time(grid, steps, 1);
    let base_mean = mean(&base_runs);

    for workers in 1..=max_workers {

        let runs = measure_time(grid, steps, workers);

        let m = mean(&runs);
        let sd = std_dev(&runs, m);
        let out = outlier(&runs, m);

        let speedup = base_mean / m;

        results.push(ResultRow {
            workers,
            mean: speedup,
            std_dev: sd,
            outlier: out,
        });
    }

    results
}

pub fn weak_scaling_rust(
    base_grid_size: usize,
    steps: usize
) -> Vec<ResultRow> {

    let max_workers = num_cpus::get();
    let mut results = vec![];

    let base_grid = Grid::new(base_grid_size, base_grid_size);
    let base_runs = measure_time(&base_grid, steps, 1);
    let base_mean = mean(&base_runs);

    for workers in 1..=max_workers {

        let scaled_grid =
            Grid::new(base_grid_size * workers, base_grid_size);

        let runs = measure_time(&scaled_grid, steps, workers);

        let m = mean(&runs);
        let sd = std_dev(&runs, m);
        let out = outlier(&runs, m);

        let efficiency = base_mean / m;

        results.push(ResultRow {
            workers,
            mean: efficiency,
            std_dev: sd,
            outlier: out,
        });
    }

    results
}


pub fn plot_strong(
    data: &[ResultRow]
) -> Result<(), Box<dyn std::error::Error>> {

    let root = BitMapBackend::new("strong_scaling.png", (1024, 768))
        .into_drawing_area();
    root.fill(&WHITE)?;

    let max_workers = data.iter().map(|r| r.workers).max().unwrap();

    let mut chart = ChartBuilder::on(&root)
        .caption("Strong Scaling", ("sans-serif", 40))
        .margin(20)
        .x_label_area_size(40)
        .y_label_area_size(60)
        .build_cartesian_2d(1..max_workers, 0.0..max_workers as f64)?;

    chart.configure_mesh()
        .x_desc("Workers")
        .y_desc("Speedup")
        .draw()?;

    // Observed
    chart.draw_series(LineSeries::new(
        data.iter().map(|r| (r.workers, r.mean)),
        &RED,
    ))?;

    // Ideal
    chart.draw_series(LineSeries::new(
        (1..=max_workers).map(|w| (w, w as f64)),
        &BLACK,
    ))?;

    Ok(())
}

pub fn plot_weak(
    data: &[ResultRow]
) -> Result<(), Box<dyn std::error::Error>> {

    let root = BitMapBackend::new("weak_scaling.png", (1024, 768))
        .into_drawing_area();
    root.fill(&WHITE)?;

    let max_workers = data.iter().map(|r| r.workers).max().unwrap();

    let mut chart = ChartBuilder::on(&root)
        .caption("Weak Scaling", ("sans-serif", 40))
        .margin(20)
        .x_label_area_size(40)
        .y_label_area_size(60)
        .build_cartesian_2d(1..max_workers, 0.0..1.2)?;

    chart.configure_mesh()
        .x_desc("Workers")
        .y_desc("Efficiency")
        .draw()?;

    // Observed
    chart.draw_series(LineSeries::new(
        data.iter().map(|r| (r.workers, r.mean)),
        &BLUE,
    ))?;

    // Ideal efficiency = 1
    chart.draw_series(LineSeries::new(
        (1..=max_workers).map(|w| (w, 1.0)),
        &BLACK,
    ))?;

    Ok(())
}


pub fn plot_scaling(
    strong: &[(usize, f64)],
    weak: &[(usize, f64)]
) -> Result<(), Box<dyn std::error::Error>> {

    let root = BitMapBackend::new("scaling.png", (1024, 768))
        .into_drawing_area();
    root.fill(&WHITE)?;

    let max_workers = strong.iter().map(|(w, _)| *w).max().unwrap_or(1);
    let max_val = strong.iter()
        .map(|(_, s)| *s)
        .fold(0./0., f64::max)
        .max(
            weak.iter()
                .map(|(_, e)| *e)
                .fold(0./0., f64::max)
        );

    let mut chart = ChartBuilder::on(&root)
        .caption("Strong vs Weak Scaling", ("sans-serif", 40))
        .margin(20)
        .x_label_area_size(40)
        .y_label_area_size(60)
        .build_cartesian_2d(1..max_workers, 0.0..max_val)?;

    chart.configure_mesh()
        .x_desc("Workers")
        .y_desc("Speedup / Efficiency")
        .draw()?;

    chart.draw_series(LineSeries::new(
        strong.iter().map(|(w, s)| (*w, *s)),
        &RED,
    ))?.label("Strong (Speedup)")
      .legend(|(x, y)| PathElement::new([(x, y), (x+20, y)], &RED));

    chart.draw_series(LineSeries::new(
        weak.iter().map(|(w, e)| (*w, *e)),
        &BLUE,
    ))?.label("Weak (Efficiency)")
      .legend(|(x, y)| PathElement::new([(x, y), (x+20, y)], &BLUE));

    chart.configure_series_labels()
        .background_style(&WHITE.mix(0.8))
        .border_style(&BLACK)
        .draw()?;

    Ok(())
}
pub fn print_table(title: &str, data: &[ResultRow]) {

    println!("\n=== {} ===", title);
    println!(
        "{:<8} {:<12} {:<12} {:<12}",
        "Workers", "Mean", "Std Dev", "Outlier"
    );

    for r in data {
        println!(
            "{:<8} {:<12.3} {:<12.3} {:<12.3}",
            r.workers, r.mean, r.std_dev, r.outlier
        );
    }
}

pub fn strong_scaling_raw_table(grid: &Grid, steps: usize)
    -> Vec<(usize, Vec<f64>)>
{
    let workers_list = [0, 1, 2, 4, 8]; // 0 = serial
    let runs = 30;

    let mut results = Vec::new();

    for &workers in &workers_list {
        let mut times = Vec::with_capacity(runs);

        for _ in 0..runs {
            let mut g = grid.clone();

            let start = std::time::Instant::now();

            for _ in 0..steps {
                if workers == 0 {
                    g.step_sequential();
                } else {
                    g.step_parallel(workers);
                }
            }

            times.push(start.elapsed().as_secs_f64());
        }

        results.push((workers, times));
    }

    results
}

pub fn print_raw_table(data: &[(usize, Vec<f64>)]) {
    println!("Run | Serial | 1T | 2T | 4T | 8T");
    println!("-----------------------------------");

    let runs = data[0].1.len();

    for i in 0..runs {
        print!("{:>3} |", i + 1);

        for (_, times) in data {
            print!(" {:>7.3} |", times[i]);
        }

        println!();
    }
}
pub fn weak_scaling_raw_table(
    base_grid_size: usize,
    steps: usize,
) -> Vec<(usize, Vec<f64>)> {

    let workers_list = [1, 2, 4, 8];
    let runs = 30;

    let mut results = Vec::new();

    for &workers in &workers_list {

        // Scale grid with workers
        let grid = Grid::new(base_grid_size * workers, base_grid_size);

        let mut times = Vec::with_capacity(runs);

        for _ in 0..runs {

            let mut g = grid.clone();

            let start = std::time::Instant::now();

            for _ in 0..steps {
                g.step_parallel(workers);
            }

            times.push(start.elapsed().as_secs_f64());
        }

        results.push((workers, times));
    }

    results
}

pub fn print_weak_raw_table(data: &[(usize, Vec<f64>)]) {

    println!("Run | 1T | 2T | 4T | 8T");
    println!("-------------------------");

    let runs = data[0].1.len();

    for i in 0..runs {
        print!("{:>3} |", i + 1);

        for (_, times) in data {
            print!(" {:>7.3} |", times[i]);
        }

        println!();
    }
}
