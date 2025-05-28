import os
import shutil
import random
from pathlib import Path
from collections import defaultdict

def get_class_distribution(labels_dir):
    """Get distribution of classes in a labels directory"""
    class_counts = defaultdict(int)
    for label_file in Path(labels_dir).glob('*.txt'):
        with open(label_file, 'r') as f:
            for line in f:
                class_id = int(line.split()[0])
                class_counts[class_id] += 1
    return class_counts

def collect_files(base_dir):
    """Collect all image and label files with their class distributions"""
    data = {
        'images': [],
        'labels': [],
        'class_dist': defaultdict(int)
    }
    
    print(f"\nSearching for files in: {base_dir}")
    
    # First, find all label files
    for split in ['train', 'valid', 'test']:
        labels_dir = Path(base_dir) / split / 'labels'
        if not labels_dir.exists():
            print(f"Warning: {labels_dir} does not exist")
            continue
            
        print(f"\nProcessing {split} split...")
        for label_file in labels_dir.glob('*.txt'):
            # Construct image path - images are in the same split's images directory
            img_file = Path(base_dir) / split / 'images' / label_file.with_suffix('.jpg').name
            print(f"Looking for image at: {img_file}")
            
            if img_file.exists():
                print(f"Found matching image: {img_file}")
                data['labels'].append(str(label_file))
                data['images'].append(str(img_file))
                
                # Count classes in this file
                with open(label_file, 'r') as f:
                    for line in f:
                        class_id = int(line.split()[0])
                        data['class_dist'][class_id] += 1
            else:
                print(f"Warning: No matching image found for {label_file}")
    
    return data

def reshuffle_dataset(original_dir, train_ratio=0.7, val_ratio=0.15, test_ratio=0.15):
    """Reshuffle dataset ensuring balanced class distribution"""
    # Create new directory with _reshuffled suffix
    new_dir = Path(original_dir).parent / f"{Path(original_dir).name}_reshuffled"
    print(f"\nCreating new directory at: {new_dir}")
    
    # Create directory structure
    splits = ['train', 'valid', 'test']
    for split in splits:
        for subdir in ['images', 'labels']:
            dir_path = new_dir / split / subdir
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"Created directory: {dir_path}")
    
    # Copy data.yaml if it exists
    yaml_file = Path(original_dir) / 'data.yaml'
    if yaml_file.exists():
        shutil.copy2(yaml_file, new_dir / 'data.yaml')
        print(f"Copied data.yaml to {new_dir}")
    
    # Collect all files from original directory
    print("\nCollecting files from original directory...")
    data = collect_files(original_dir)
    
    if not data['images']:
        print("Error: No image-label pairs found!")
        print("Please check the directory structure and file paths.")
        return
    
    print(f"Found {len(data['images'])} image-label pairs")
    print("Initial class distribution:")
    for class_id, count in sorted(data['class_dist'].items()):
        print(f"Class {class_id}: {count}")
    
    # Group files by class
    print("\nGrouping files by class...")
    class_files = defaultdict(list)
    for img, label in zip(data['images'], data['labels']):
        with open(label, 'r') as f:
            classes = set(int(line.split()[0]) for line in f)
            for class_id in classes:
                class_files[class_id].append((img, label))
    
    print("Files per class:")
    for class_id, files in class_files.items():
        print(f"Class {class_id}: {len(files)} files")
    
    # Distribute files
    print("\nDistributing files...")
    for class_id, files in class_files.items():
        print(f"\nProcessing class {class_id}")
        random.shuffle(files)
        n_files = len(files)
        
        # Calculate split indices
        train_idx = int(n_files * train_ratio)
        val_idx = int(n_files * (train_ratio + val_ratio))
        
        # Split files
        splits = {
            'train': files[:train_idx],
            'valid': files[train_idx:val_idx],
            'test': files[val_idx:]
        }
        
        # Copy files to their new locations
        for split_name, split_files in splits.items():
            print(f"Copying {len(split_files)} files to {split_name}")
            for img, label in split_files:
                # Copy image
                dest_img = new_dir / split_name / 'images' / Path(img).name
                print(f"Copying image: {img} -> {dest_img}")
                shutil.copy2(img, dest_img)
                
                # Copy label
                dest_label = new_dir / split_name / 'labels' / Path(label).name
                print(f"Copying label: {label} -> {dest_label}")
                shutil.copy2(label, dest_label)
    
    # Print final class distribution in each split
    print("\nFinal class distribution in new directory:")
    for split in ['train', 'valid', 'test']:
        print(f"\nClass distribution in {split}:")
        dist = get_class_distribution(new_dir / split / 'labels')
        for class_id, count in sorted(dist.items()):
            print(f"Class {class_id}: {count}")
    
    print(f"\nReshuffled dataset created at: {new_dir}")
    print("Original dataset remains unchanged at:", original_dir)

if __name__ == "__main__":
    # Use the correct path to your dataset
    dataset_path = "bro this idc pmo.v2i.yolov8"
    
    # Add error checking
    if not os.path.exists(dataset_path):
        print(f"Error: Dataset directory '{dataset_path}' not found!")
        print("Please make sure the path is correct and the directory exists.")
        exit(1)
    
    print(f"Found dataset at: {os.path.abspath(dataset_path)}")
    print("Current working directory:", os.getcwd())
    print("Contents of dataset directory:", os.listdir(dataset_path))
    
    reshuffle_dataset(dataset_path)
