import argparse
import os
import hashlib as h


class FileHandler:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description='Show me the way!')
        self.parser.add_argument('path', default=None, nargs='?')
        self.path = self.parser.parse_args().path
        self.format = None
        self.desc = None
        self.size_dict = {}

    def run(self):
        parameters = self.init_params(self.path)
        if parameters is None:
            return
        self.format, self.desc = parameters

        # create a list of files with the same resolution and size
        self.size_dict = self.get_format_files(self.path, self.format)
        self.print_result(self.size_dict, self.desc)

        # listing duplicates
        if not self.ask_next("Check for duplicates?"):
            return
        duplicate_dict = self.get_duplicate_files(
            self.size_dict,
            self.desc
        )
        n_duplicates = self.print_duplicates(duplicate_dict)

        # deleting duplicates
        if not self.ask_next("Delete files?"):
            return
        free_size = self.delete_duplicates(duplicate_dict, n_duplicates)
        print(f"\nTotal freed up space: {free_size} bytes")

    # ---------- Init params for printing ----------

    def init_params(self, path):
        is_desc = None
        if not path:
            print("Directory is not specified")
            return None
        file_format = input("Enter file format:\n")
        print(
            "Size sorting options:\n"
            "1. Descending\n"
            "2. Ascending"
        )
        while is_desc is None:
            sorting = input("Enter a sorting option:\n")
            if sorting in ("1", "2"):
                is_desc = True if sorting == "1" else False
            else:
                print("Wrong option")
        return file_format, is_desc

    # ---------- deleting duplicates ----------

    def delete_duplicates(self, duplicate_dict, n):
        number = 1
        size = 0
        del_indexes = self.get_delete_indexes(n)
        for k, v in duplicate_dict.items():
            files = [file for f_list in v.values() for file in f_list]
            for file in files:
                if number in del_indexes:
                    os.remove(file)
                    size += int(k)
                number += 1
        return size

    def get_delete_indexes(self, n):
        while True:
            try:
                input_ids = input("\nEnter file numbers to delete:\n")
                if not input_ids:
                    raise ValueError
                input_ids = list(map(int, input_ids.split()))
                if all(i in range(1, n + 1) for i in input_ids):
                    return input_ids
                raise ValueError
            except ValueError:
                print("Wrong format")

    # ---------- listing duplicates ----------

    def get_file_hash(self, file):
        m = h.md5()
        with open(file, "rb") as f:
            for line in f:
                m.update(line)
        return m.hexdigest()

    def get_duplicate_files(self, files_dict, is_desc):
        duplicat_dict = {}
        for k, v in files_dict.items():
            hash_dict = {}
            for f in v:
                file_hash = self.get_file_hash(f)
                hash_dict.setdefault(file_hash, []).append(f)
            filtered_hash = {
                k: v for k, v in hash_dict.items() if len(v) > 1
            }
            duplicat_dict[k] = filtered_hash
        return dict(sorted(duplicat_dict.items(), reverse=is_desc))

    def print_duplicates(self, duplicate_dict):
        n = 1
        for k, v in duplicate_dict.items():
            print(f"\n{k} bytes")
            for f_hash, files in v.items():
                print(f"Hash: {f_hash}")
                for f in files:
                    print(f"{n}. {f}")
                    n += 1
        return n - 1

    # ---------- same resolution and size files ----------

    def get_format_files(self, root_path, file_format):
        files_dict = {}
        for address, _, files in os.walk(root_path):
            for name in files:
                if not file_format or name.endswith(file_format):
                    path = os.path.join(address, name)
                    size = os.path.getsize(path)
                    files_dict.setdefault(size, []).append(path)
        return {k: v for k, v in files_dict.items() if len(v) > 1}

    def print_result(self, dict_print, is_desc):
        items = sorted(dict_print.items(), reverse=is_desc)
        for k, v in items:
            print(f"\n{k} bytes")
            print(*v, sep="\n")

    # ---------- helpers ----------

    def ask_next(self, question):
        answer = None
        while answer not in ("yes", "no"):
            answer = input(f"\n{question}\n")
            if answer in ("yes", "no"):
                if answer == "no":
                    return False
                break
            print("Wrong option")
        return True


def main():
    file_handler = FileHandler()
    file_handler.run()


if __name__ == "__main__":
    main()
