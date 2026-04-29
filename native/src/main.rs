mod parser;
mod runner;
mod task;

use std::fs;
use std::io::{Read, Write};
use std::net::{TcpListener, TcpStream};
use std::path::Path;
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;

use parser::{parse_progress, parse_recovered_files};
use task::{TaskManager, TaskStatus};

fn main() {
    let listener = TcpListener::bind("127.0.0.1:8787").expect("bind failed");
    let manager = Arc::new(Mutex::new(TaskManager::default()));
    println!("Recovery Assistant Native running at http://127.0.0.1:8787");

    for stream in listener.incoming() {
        let manager = Arc::clone(&manager);
        if let Ok(stream) = stream {
            thread::spawn(move || handle_connection(stream, manager));
        }
    }
}

fn handle_connection(mut stream: TcpStream, manager: Arc<Mutex<TaskManager>>) {
    let mut buffer = [0; 8192];
    if stream.read(&mut buffer).is_err() {
        return;
    }
    let req = String::from_utf8_lossy(&buffer);
    let first = req.lines().next().unwrap_or("");

    if first.starts_with("GET / ") {
        respond_file(&mut stream, "native/static/index.html", "text/html");
    } else if first.starts_with("GET /app.js ") {
        respond_file(&mut stream, "native/static/app.js", "application/javascript");
    } else if first.starts_with("GET /style.css ") {
        respond_file(&mut stream, "native/static/style.css", "text/css");
    } else if first.starts_with("POST /api/scan ") {
        let task_id = {
            let mut lock = manager.lock().unwrap();
            lock.create("scan queued")
        };
        let manager2 = Arc::clone(&manager);
        let tid = task_id.clone();
        thread::spawn(move || {
            for pct in (0..=100).step_by(10) {
                let line = format!("Pass 1 - {}%", pct);
                let progress = parse_progress(&line).unwrap_or(pct as f32);
                let mut lock = manager2.lock().unwrap();
                lock.update_progress(&tid, progress, "scanning");
                lock.append_log(&tid, &line);
                drop(lock);
                thread::sleep(Duration::from_millis(120));
            }
            let output = "Recovered: /recup/f1.jpg (100 bytes)\nRecovered: /recup/f2.pdf (200 bytes)";
            let result = parse_recovered_files(output);
            let mut lock = manager2.lock().unwrap();
            lock.finish(&tid, result);
        });
        respond_json(&mut stream, &format!("{{\"task_id\":\"{}\"}}", task_id));
    } else if first.starts_with("GET /api/task/") {
        let path = first.split_whitespace().nth(1).unwrap_or("/");
        let tid = path.trim_start_matches("/api/task/");
        let body = {
            let lock = manager.lock().unwrap();
            lock.to_json(tid)
        };
        respond_json(&mut stream, &body.unwrap_or_else(|| "{\"error\":\"not found\"}".to_string()));
    } else {
        respond_404(&mut stream);
    }
}

fn respond_file(stream: &mut TcpStream, file: &str, content_type: &str) {
    if let Ok(content) = fs::read_to_string(Path::new(file)) {
        let response = format!(
            "HTTP/1.1 200 OK\r\nContent-Type: {}; charset=utf-8\r\nContent-Length: {}\r\n\r\n{}",
            content_type,
            content.len(),
            content
        );
        let _ = stream.write_all(response.as_bytes());
    } else {
        respond_404(stream);
    }
}

fn respond_json(stream: &mut TcpStream, body: &str) {
    let response = format!(
        "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {}\r\n\r\n{}",
        body.len(), body
    );
    let _ = stream.write_all(response.as_bytes());
}

fn respond_404(stream: &mut TcpStream) {
    let body = "Not Found";
    let response = format!("HTTP/1.1 404 NOT FOUND\r\nContent-Length: {}\r\n\r\n{}", body.len(), body);
    let _ = stream.write_all(response.as_bytes());
}
