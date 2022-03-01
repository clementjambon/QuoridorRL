def write_history(output_path: str, history):
    with open(output_path, 'w') as f:
        for record in history:
            f.write(record + '\n')


def read_history(path: str):
    with open(path, 'r') as f:
        return f.read().splitlines()
