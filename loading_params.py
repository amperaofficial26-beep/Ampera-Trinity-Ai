JUMLAH_PARAM_PER_LOADING = 5   # 5 x 5 detik = 25 detik total per putaran
DURASI_PER_PARAM_MS = 5000     # 5 detik per parameterNAMA_PARAMETER = [
    "temperature", "top-k", "top-p", "max_tokens",
    "presence_penalty", "frequency_penalty", "seed", "min_p",
    "stop_sequences", "repetition_penalty", "typical_p", "mirostat",
    "batch_size", "vram", "quantization", "gpu_layers",
    "tensor_parallel_size", "num_threads",
]
def pilih_parameter(jumlah: int = JUMLAH_PARAM_PER_LOADING) -> list[int]:
    """Ambil acak `jumlah` indeks parameter tanpa duplikat."""
    return random.sample(range(len(NAMA_PARAMETER)), jumlah)
