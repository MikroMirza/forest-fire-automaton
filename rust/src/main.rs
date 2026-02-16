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
use rand::Rng;

#[repr(u8)]
#[derive(Debug, Copy, Clone, PartialEq)]
enum PixelState {
    Empty = 0,
    Tree = 1,
    Burning = 2,
    ThickTree = 3,
}

fn color_of(state: PixelState) -> (u8, u8, u8) {
    match state {
        PixelState::Empty => (0, 0, 0),
        PixelState::Tree => (34, 139, 34),
        PixelState::Burning => (255, 69, 0),
        PixelState::ThickTree => (31, 129, 31),
    }
}

const GROWTH_CHANCE: f32 = 0.01;
const LIGHTNING_CHANCE: f32 = 0.0001;
const FIRE_SPREAD_CHANCE: f32 = 0.3;

struct Grid {
    rows: usize,
    cols: usize,
    data: Vec<PixelState>,
}

impl Grid {
    fn new(rows: usize, cols: usize) -> Self {
        Grid {
            rows,
            cols,
            data: vec![PixelState::Tree; rows * cols],
        }
    }

    fn index(&self, row: usize, col: usize) -> usize {
        row * self.cols + col
    }

    fn get(&self, row: usize, col: usize) -> PixelState {
        self.data[self.index(row, col)]
    }

    fn set(&mut self, row: usize, col: usize, value: PixelState) {
        let idx = self.index(row, col);
        self.data[idx] = value;
    }

    fn step(&mut self) {
        let mut rng = rand::thread_rng();
        let mut new_data = self.data.clone();

        for row in 0..self.rows {
            for col in 0..self.cols {
                let idx = self.index(row, col);
                let cell = self.data[idx];

                match cell {
                    PixelState::Burning => {
                        new_data[idx] = PixelState::Empty;
                    }
                    PixelState::Tree | PixelState::ThickTree => {
                        let mut on_fire = false;
                        for dy in [-1isize, 0, 1] {
                            for dx in [-1isize, 0, 1] {
                                if dy == 0 && dx == 0 { continue; }
                                let ny = row as isize + dy;
                                let nx = col as isize + dx;
                                if ny >= 0 && ny < self.rows as isize && nx >= 0 && nx < self.cols as isize {
                                    let n_idx = self.index(ny as usize, nx as usize);
                                    if self.data[n_idx] == PixelState::Burning && rng.random::<f32>() < FIRE_SPREAD_CHANCE {
                                        on_fire = true;
                                    }
                                }
                            }
                        }

                        if rng.random::<f32>() < LIGHTNING_CHANCE {
                            on_fire = true;
                        }

                        if on_fire {
                            new_data[idx] = PixelState::Burning;
                        }
                    }
                    PixelState::Empty => {
                        if rng.random::<f32>() < GROWTH_CHANCE {
                            new_data[idx] = PixelState::Tree;
                        }
                    }
                }
            }
        }

        self.data = new_data;
    }
}

fn main() {
    let mut grid = Grid::new(512, 512);

    grid.set(100, 100, PixelState::Burning);

    for _ in 0..10 {
        grid.step();
    }

    println!("Cell (100,100): {:?}", grid.get(100, 100));
}
