import os
import shutil
import tempfile

def clean_file_in_place(filepath):

    temp, temp_p = tempfile.mkstemp()
    
    try:
        with os.fdopen(temp, 'w', encoding='utf-8') as temp_file:
            with open(filepath, 'r', encoding='utf-8') as original_file:
                is_header_block = False
                
                for line in original_file:
                    stripped_line = line.strip()

                    if '---' in stripped_line or stripped_line.startswith('Page '):
                        if not is_header_block:
                            temp_file.write('#\n')
                            is_header_block = True

                    elif stripped_line:
                        temp_file.write(line)
                        is_header_block = False

        shutil.move(temp_p, filepath)
        return True 
        
    except Exception as e:
        print(f"Error processing {os.path.basename(filepath)}: {e}")
        os.remove(temp_p)
        return False

def clean_directory(directory_path):
    if not os.path.isdir(directory_path):
        print(f"❌ Error: Directory not found at '{directory_path}'")
        return

    files_found = 0
    for filename in os.listdir(directory_path):
        if filename.endswith(".txt"):
            files_found += 1
            full_path = os.path.join(directory_path, filename)
            clean_file_in_place(full_path)
    
    if files_found == 0:
        print("\nNo .txt files were found to clean.")
    

if __name__ == "__main__":
    # Change the path depending upon where your text files are stored
    target_directory = '../data/texts'

    clean_directory(target_directory)