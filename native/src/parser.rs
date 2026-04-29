#[derive(Clone, Debug)]
pub struct RecoveryFile {
    pub path: String,
    pub name: String,
    pub ext: String,
    pub size: u64,
}

#[derive(Clone, Debug, Default)]
pub struct ScanResult {
    pub files: Vec<RecoveryFile>,
}

pub fn parse_progress(line: &str) -> Option<f32> {
    let marker = "%";
    if !line.contains("Pass") || !line.contains(marker) {
        return None;
    }
    let num = line.split_whitespace().last()?.trim_end_matches('%');
    num.parse::<f32>().ok().map(|v| v.clamp(0.0, 100.0))
}

pub fn parse_recovered_files(output: &str) -> ScanResult {
    let mut result = ScanResult::default();
    for line in output.lines() {
        if !line.starts_with("Recovered: ") { continue; }
        let body = line.trim_start_matches("Recovered: ");
        let parts: Vec<&str> = body.rsplitn(2, " (").collect();
        if parts.len() != 2 { continue; }
        let size = parts[0].trim_end_matches(" bytes)").parse::<u64>().unwrap_or(0);
        let path = parts[1].trim().to_string();
        let name = path.split('/').last().unwrap_or("").to_string();
        let ext = name.split('.').last().unwrap_or("").to_lowercase();
        result.files.push(RecoveryFile { path, name, ext, size });
    }
    result
}
