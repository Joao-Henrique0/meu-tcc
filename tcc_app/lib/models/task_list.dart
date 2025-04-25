import 'dart:math';
import 'package:flutter/material.dart';
import 'package:tcc_app/utils/db_util.dart';
import 'task.dart';
import 'package:tcc_app/components/notification.dart';

class TaskList with ChangeNotifier {
  List<Task> _tasks = [];

  List<Task> get tasks {
    // Ordena as tarefas por tempo antes de retornar
    _tasks.sort((a, b) => a.time.compareTo(b.time));
    return [..._tasks];
  }

  int get itensCount {
    return _tasks.length;
  }

  Future<void> loadTasks() async {
    final dataList = await DbUtil.getData('tasks');
    _tasks =
        dataList
            .map(
              (item) => Task(
                id: item['id'],
                title: item['title'],
                description: item['description'],
                time: DateTime.parse(item['time']),
                complete: item['complete'] == 1 ? true : false,
              ),
            )
            .toList();
    notifyListeners();
  }

  Task itemByIndex(int index) {
    return _tasks[index];
  }

  Future<void> saveTask(Map<String, Object> data) async {
    bool hasId = data['id'] != null;
    final task = Task(
      id: hasId ? data['id'] as String : Random().nextInt(420000000).toString(),
      title: data['title'] as String,
      description: data['description'] as String,
      time: data['time'] as DateTime,
      complete: false,
    );
    //  FirebaseNotificationService.scheduleNotification(
    //   task.title,
    //   task.description,
    //   task.time,
    //   task.id,
    // );
    // if (hasId) {
    //   await updateTask(task);
    // } else {
    //   await addTask(task);
    // }
  }

  Future<void> updateTask(Task task) async {
    int index = _tasks.indexWhere((t) => t.id == task.id);
    if (index >= 0) {
      _tasks[index] = task;
      notifyListeners();
      await DbUtil.updateData('tasks', {
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'time': task.time.toString(),
        'complete': task.complete ? 1 : 0,
      });
    }
  }

  Future<void> addTask(Task task) async {
    await DbUtil.insertData('tasks', {
      'id': task.id,
      'title': task.title,
      'description': task.description,
      'time': task.time.toIso8601String(),
      'complete': task.complete ? 1 : 0,
    });
    _tasks.add(task);
    notifyListeners();
  }

  Future<void> removeTask(Task task) async {
    int index = _tasks.indexWhere((t) => t.id == task.id);
    if (index >= 0) {
      _tasks.removeAt(index);
      notifyListeners();
      await DbUtil.deleteData('tasks', task.id);
    }
  }

  Future<void> updateTaskComplete(String taskId, bool complete) async {
    // Atualiza o status de conclusão da tarefa no banco de dados
    await DbUtil.updateComplete(taskId, complete);

    // Atualiza a tarefa na lista em memória
    final taskIndex = _tasks.indexWhere((task) => task.id == taskId);
    if (taskIndex >= 0) {
      _tasks[taskIndex].complete = complete;
      notifyListeners();
    }
  }
}
