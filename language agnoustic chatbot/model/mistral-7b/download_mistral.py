from huggingface_hub import snapshot_download

# Folder where model will be saved
local_dir = "D:/models/mistral-7b"

# Download Mistral-7B
snapshot_download(
    repo_id="mistralai/Mistral-7B-v0.1",
    local_dir=local_dir,
    revision="main"
)
