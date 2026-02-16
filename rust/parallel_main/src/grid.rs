#[repr(u8)]
#[derive(Debug, Copy, Clone, PartialEq)]
pub enum PixelState {
    Empty = 0,
    Tree = 1,
    Burning = 2,
    ThickTree = 3,
}

pub const GROWTH_CHANCE: f32 = 0.01;
pub const LIGHTNING_CHANCE: f32 = 0.0001;
pub const FIRE_SPREAD_CHANCE: f32 = 0.3;

#[derive(Clone)]
pub struct Grid {
    pub rows: usize,
    pub cols: usize,
    pub data: Vec<PixelState>,
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
        let old_data = self.data.clone();
        let mut new_data = vec![PixelState::Empty; self.rows * self.cols];

        let rows_per_thread = self.rows / NUM_OF_THREADS;
        let cols = self.cols;
        let rows = self.rows;

        thread::scope(|s| {
            let mut remaining = new_data.as_mut_slice();

            for t in 0..NUM_OF_THREADS {
                let start_row = t * rows_per_thread;
                let end_row = if t == NUM_OF_THREADS - 1 {
                    self.rows
                } else {
                    start_row + rows_per_thread
                };

                let chunk_len = (end_row - start_row) * cols;

                let (current_chunk, rest) = remaining.split_at_mut(chunk_len);
                remaining = rest;

                let old_data = &old_data;

                s.spawn(move || {
                    let mut rng = rand::thread_rng();

                    for (i, cell_out) in current_chunk.iter_mut().enumerate() {
                        let row = start_row + i / cols;
                        let col = i % cols;

                        let idx = row * cols + col;
                        let cell = old_data[idx];

                        let new_state = match cell {
                            PixelState::Burning => PixelState::Empty,

                            PixelState::Tree | PixelState::ThickTree => {
                                let mut on_fire = false;

                                for dy in [-1isize, 0, 1] {
                                    for dx in [-1isize, 0, 1] {
                                        if dy == 0 && dx == 0 { continue; }

                                        let ny = row as isize + dy;
                                        let nx = col as isize + dx;

                                        if ny >= 0 && ny < rows as isize &&
                                        nx >= 0 && nx < cols as isize {

                                            let n_idx = ny as usize * cols + nx as usize;

                                            if old_data[n_idx] == PixelState::Burning &&
                                            rng.random::<f32>() < FIRE_SPREAD_CHANCE
                                            {
                                                on_fire = true;
                                            }
                                        }
                                    }
                                }

                                if rng.random::<f32>() < LIGHTNING_CHANCE {
                                    on_fire = true;
                                }

                                if on_fire { PixelState::Burning } else { cell }
                            }

                            PixelState::Empty => {
                                if rng.random::<f32>() < GROWTH_CHANCE {
                                    PixelState::Tree
                                } else {
                                    PixelState::Empty
                                }
                            }
                        };

                        *cell_out = new_state;
                    }
                });
            }
        });

        std::mem::swap(&mut self.data, &mut new_data);
    }


}
