import shutil
 


 
# Example usage
for i in range(2,18,2):
    for j in ['c', 'p']:
        source_file = f"lsd_{j}_{i}_workingfinal"
        new_file = f"lsd_{j}_{i}_production"        
        shutil.copytree(source_file, new_file, dirs_exist_ok=True)