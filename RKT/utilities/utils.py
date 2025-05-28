def save_to_env_file(key, value):
    with open(".env", "a") as f:  # Append mode
        f.write(f"{key}={value}\n")
