import 'package:flutter/material.dart';

class ChatMessages extends StatelessWidget {
  const ChatMessages({super.key});

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      padding: EdgeInsets.all(10),
      itemCount: 5, // Simulação de mensagens
      itemBuilder: (context, index) {
        bool isUser = index % 2 == 0;
        return Align(
          alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
          child: Container(
            margin: EdgeInsets.symmetric(vertical: 5),
            padding: EdgeInsets.all(8),
            decoration: BoxDecoration(
              color:
                  isUser
                      ? Theme.of(context).colorScheme.secondary
                      : Colors.grey[300],
              borderRadius: BorderRadius.circular(12),
            ),
            child: Text(
              isUser ? "Olá, bot!" : "Olá! Como posso ajudar?",
              style: TextStyle(color: Colors.black),
            ),
          ),
        );
      },
    );
  }
}
