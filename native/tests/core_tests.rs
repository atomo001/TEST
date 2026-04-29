#[path = "../src/parser.rs"] mod parser;
#[path = "../src/task.rs"] mod task;
#[path = "../src/runner.rs"] mod runner;

#[test]
fn parser_progress() {
    assert_eq!(parser::parse_progress("Pass 1 - 56%"), Some(56.0));
}

#[test]
fn parser_files() {
    let r = parser::parse_recovered_files("Recovered: /recup/f1.jpg (100 bytes)");
    assert_eq!(r.files.len(), 1);
    assert_eq!(r.files[0].ext, "jpg");
}

#[test]
fn task_lifecycle() {
    let mut m = task::TaskManager::default();
    let id = m.create("init");
    m.update_progress(&id, 10.0, "scan");
    m.finish(&id, parser::ScanResult::default());
    assert!(m.to_json(&id).unwrap().contains("completed"));
}

#[test]
fn command_run() {
    let out = runner::run_command("python", &["-c", "print('ok')"]).unwrap();
    assert!(out.contains("ok"));
}
