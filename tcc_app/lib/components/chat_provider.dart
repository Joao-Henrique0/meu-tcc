import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:tcc_app/models/chat_message.dart';
import 'package:tcc_app/models/task.dart';
import 'package:tcc_app/models/task_list.dart';

class ChatProvider with ChangeNotifier {
  final List<ChatMessage> _messages = [];

  List<ChatMessage> get messages => List.unmodifiable(_messages);

  ChatProvider() {
    loadMessages();
  }

  Future<void> loadMessages() async {
    final prefs = await SharedPreferences.getInstance();
    final saved = prefs.getStringList('chat_messages') ?? [];
    _messages.clear();
    _messages.addAll(saved.map((e) => ChatMessage.fromJson(json.decode(e))));
    notifyListeners();
  }

  Future<void> saveMessages() async {
    final prefs = await SharedPreferences.getInstance();
    final toSave = _messages.map((e) => json.encode(e.toJson())).toList();
    await prefs.setStringList('chat_messages', toSave);
  }

  Future<void> sendMessage(String userMessage, BuildContext context) async {
    if (userMessage.trim().isEmpty) return;

    _messages.add(ChatMessage(text: userMessage, isUser: true));
    notifyListeners();
    await saveMessages();

    try {
      final session = Supabase.instance.client.auth.currentSession;
      final token = session?.accessToken;

      if (token == null) {
        _messages.add(
          ChatMessage(text: "Usuário não autenticado.", isUser: false),
        );
        notifyListeners();
        await saveMessages();
        return;
      }

      final response = await http.post(
        Uri.parse('http://10.0.2.2:5000/chatbot'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: jsonEncode({"message": userMessage}),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final responseData = data["response"];
        final intent = responseData?["intent"];
        final taskData = responseData?["data"];
        final taskList = Provider.of<TaskList>(context, listen: false);
        print("Data received: $data");

        switch (intent) {
          case "adicionar_tarefa":
            if (taskData != null) {
              final newTask = Task(
                id: DateTime.now().millisecondsSinceEpoch.toString(),
                title: taskData["title"],
                description: taskData["description"],
                time: DateTime.parse(taskData["time"]),
                complete: false,
              );
              await taskList.addTask(newTask);

              _messages.add(
                ChatMessage(
                  text: "Tarefa ${newTask.title} adicionada com sucesso!",
                  isUser: false,
                ),
              );
            } else {
              _messages.add(
                ChatMessage(
                  text: data["error"] ?? "Não consegui entender a tarefa.",
                  isUser: false,
                ),
              );
            }
            break;

          case "listar_tarefas":
            final tarefas = taskList.tasks;
            if (tarefas.isEmpty) {
              _messages.add(
                ChatMessage(
                  text: "Você não possui tarefas no momento.",
                  isUser: false,
                ),
              );
            } else {
              final texto = tarefas
                  .map((t) {
                    final status = t.complete ? "✅" : "🔘";
                    return "$status ${t.title} às ${t.time}";
                  })
                  .join("\n");

              _messages.add(ChatMessage(text: texto, isUser: false));
            }
            break;

          case "deletar_tarefa":
            if (taskData != null && taskData["title"] != null) {
              final title = taskData["title"];
              try {
                final task = taskList.tasks.firstWhere(
                  (t) => t.title.toLowerCase() == title.toLowerCase(),
                );

                if (task.id.isNotEmpty) {
                  await taskList.removeTask(task);
                  _messages.add(
                    ChatMessage(
                      text: "Tarefa '${task.title}' removida com sucesso!",
                      isUser: false,
                    ),
                  );
                } else {
                  _messages.add(
                    ChatMessage(
                      text:
                          responseData["error"] ??
                          "Informe o nome da tarefa a ser removida.",
                      isUser: false,
                    ),
                  );
                }
              } catch (e) {
                _messages.add(
                  ChatMessage(
                    text: "Tarefa '$title' não encontrada.",
                    isUser: false,
                  ),
                );
              }
            }
            break;

          case "atualizar_tarefa":
            if (taskData != null && taskData["title"] != null) {
              try {
                final task = taskList.tasks.firstWhere(
                  (t) =>
                      t.title.toLowerCase() == taskData["title"].toLowerCase(),
                );

                if (task.id.isNotEmpty) {
                  final updated = Task(
                    id: task.id,
                    title: task.title,
                    description: task.description,
                    time: DateTime.parse(taskData["new_time"]),
                    complete: task.complete,
                  );

                  await taskList.updateTask(updated);

                  _messages.add(
                    ChatMessage(
                      text:
                          "Tarefa '${task.title}' atualizada para ${updated.time}.",
                      isUser: false,
                    ),
                  );
                } else {
                  _messages.add(
                    ChatMessage(
                      text:
                          responseData["error"] ??
                          "Informe o nome da tarefa a ser atualizada.",
                      isUser: false,
                    ),
                  );
                }
              } catch (e) {
                _messages.add(
                  ChatMessage(
                    text: "Tarefa '${taskData["title"]}' não encontrada.",
                    isUser: false,
                  ),
                );
              }
            }
            break;

          case "saudacao":
            print("Saudação recebida");
            print(data);
            _messages.add(
              ChatMessage(text: responseData["text"] ?? "Olá!", isUser: false),
            );
            break;
          case "despedida":
            _messages.add(
              ChatMessage(
                text: responseData["text"] ?? "Tchau!",
                isUser: false,
              ),
            );
            break;

          default:
            _messages.add(
              ChatMessage(
                text:
                    "Comando reconhecido: $intent, mas não implementado no app.",
                isUser: false,
              ),
            );
        }
      } else {
        _messages.add(
          ChatMessage(
            text: "Erro no servidor: ${response.statusCode}",
            isUser: false,
          ),
        );
      }
    } catch (e) {
      _messages.add(
        ChatMessage(text: "Erro ao enviar mensagem: $e", isUser: false),
      );
    }

    notifyListeners();
    await saveMessages();
  }

  Future<void> deleteMessage(int index) async {
    if (index < 0 || index >= _messages.length) return;
    _messages.removeAt(index);
    notifyListeners();
    await saveMessages();
  }

  Future<void> clearAllMessages() async {
    _messages.clear();
    notifyListeners();
    await saveMessages();
  }
}
