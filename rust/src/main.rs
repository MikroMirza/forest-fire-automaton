use minifb::{Key, Window, WindowOptions};
use rand::Rng;
use std::time::Duration;
use grid_lib::*;

fn main() {
    let mut grid = Grid::new(1024, 1024);
    grid.set(100, 100, PixelState::Burning);

    let mut window = Window::new(
        "Forest Fire",
        2048,
        2048,
        WindowOptions::default(),
    ).unwrap();

    let mut buffer = vec![0u32; 2048 * 2048];

    while window.is_open() && !window.is_key_down(Key::Escape) {

        grid.step_sequential();


        for row in 0..grid.rows {
            for col in 0..grid.cols {
                let (r, g, b) = color_of(grid.get(row, col));
                let idx = row * grid.cols + col;

                buffer[idx] = ((r as u32) << 16)
                            | ((g as u32) << 8)
                            | (b as u32);
            }
        }

        window.update_with_buffer(&buffer, 2048, 2048).unwrap();

        std::thread::sleep(Duration::from_millis(30));
    }
}