use std::collections::HashMap;
use std::time::{SystemTime, UNIX_EPOCH};

use crate::parser::ScanResult;

#[derive(Clone, Debug)]
pub enum TaskStatus { Pending, Running, Completed, Failed }

#[derive(Clone, Debug)]
pub struct TaskState {
    pub id: String,
    pub status: TaskStatus,
    pub progress: f32,
    pub message: String,
    pub logs: Vec<String>,
    pub result: Option<ScanResult>,
}

#[derive(Default)]
pub struct TaskManager { pub tasks: HashMap<String, TaskState> }

impl TaskManager {
    pub fn create(&mut self, message: &str) -> String {
        let id = format!("t{}", SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_millis());
        self.tasks.insert(id.clone(), TaskState { id: id.clone(), status: TaskStatus::Pending, progress: 0.0, message: message.into(), logs: vec![], result: None });
        id
    }
    pub fn update_progress(&mut self, id: &str, progress: f32, message: &str) {
        if let Some(t) = self.tasks.get_mut(id) {
            t.progress = progress;
            t.message = message.into();
            t.status = if progress >= 100.0 { TaskStatus::Completed } else { TaskStatus::Running };
        }
    }
    pub fn append_log(&mut self, id: &str, log: &str) { if let Some(t)=self.tasks.get_mut(id){ t.logs.push(log.into()); } }
    pub fn finish(&mut self, id: &str, result: ScanResult) {
        if let Some(t)=self.tasks.get_mut(id){ t.status=TaskStatus::Completed; t.progress=100.0; t.result=Some(result); }
    }
    pub fn to_json(&self, id: &str) -> Option<String> {
        let t = self.tasks.get(id)?;
        let status = match t.status { TaskStatus::Pending=>"pending", TaskStatus::Running=>"running", TaskStatus::Completed=>"completed", TaskStatus::Failed=>"failed"};
        let logs = t.logs.iter().map(|l| format!("\"{}\"", l)).collect::<Vec<_>>().join(",");
        let files = t.result.as_ref().map(|r| r.files.iter().map(|f| format!("{{\"name\":\"{}\",\"ext\":\"{}\",\"size\":{},\"path\":\"{}\"}}", f.name, f.ext, f.size, f.path)).collect::<Vec<_>>().join(",")).unwrap_or_default();
        Some(format!("{{\"id\":\"{}\",\"status\":\"{}\",\"progress\":{},\"message\":\"{}\",\"logs\":[{}],\"result\":{{\"files\":[{}]}}}}", t.id, status, t.progress, t.message, logs, files))
    }
}
