import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:tcc_app/components/task_item.dart';
import 'package:tcc_app/models/task_list.dart';

class TasksPage extends StatelessWidget {
  const TasksPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      body: FutureBuilder(
        future: Provider.of<TaskList>(context, listen: false).loadTasks(),
        builder: (ctx, snapshot) =>
            snapshot.connectionState == ConnectionState.waiting
                ? const Center(child: CircularProgressIndicator())
                : Padding(
                    padding: const EdgeInsets.all(8),
                    child: Consumer<TaskList>(builder: (ctx, taskList, _) {
                      return taskList.itensCount == 0
                          ? const Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Text('Nenhuma tarefa cadastrada'),
                                SizedBox(height: 20),
                                SizedBox(
                                    width: double.infinity,
                                    child: Icon(
                                      Icons.content_paste_off,
                                      size: 78,
                                    ))
                              ],
                            )
                          : ListView.builder(
                              itemCount: taskList.itensCount,
                              itemBuilder: (ctx, i) => Column(
                                children: [
                                  TaskItem(task: taskList.tasks[i]),
                                ],
                              ),
                            );
                    })),
      ),
    );
  }
}
