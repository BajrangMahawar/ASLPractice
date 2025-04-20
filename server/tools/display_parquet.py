import pandas as pd
import numpy as np
import os

ROWS_PER_FRAME = 543  # Number of landmarks per frame

def load_relevant_data_subset(pq_path):
    data_columns = ['x', 'y', 'z']
    data = pd.read_parquet(pq_path, columns=data_columns)
    n_frames = int(len(data) / ROWS_PER_FRAME)
    data = data.values.reshape(n_frames, ROWS_PER_FRAME, len(data_columns))
    return data.astype(np.float32)

def save_to_csv1(data, csv_path):
    reshaped_data = []
    for frame_idx in range(data.shape[0]):
        for landmark_idx in range(data.shape[1]):
            reshaped_data.append([frame_idx, landmark_idx] + data[frame_idx, landmark_idx].tolist())
    
    flat_df = pd.DataFrame(reshaped_data, columns=["frame", "landmark_index", "x", "y", "z"])
    flat_df.to_csv(csv_path, index=False)
    print(f"Data has been written to {csv_path}")

def save_to_csv2(pq_path, csv_path):
  data = pd.read_parquet(pq_path)
  data.to_csv(csv_path, index=False)
  print(f"Data has been written to {csv_path}")


if __name__ == "__main__": 
  parquet_file = "./output/output.parquet"
  csv_file1 = os.path.splitext(parquet_file)[0] + "1.csv"
  csv_file2 = os.path.splitext(parquet_file)[0] + "2.csv"

  data = load_relevant_data_subset(parquet_file)

  save_to_csv1(data, csv_file1)
  save_to_csv2(parquet_file, csv_file2)