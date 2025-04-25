import 'package:flutter/material.dart';
import 'package:tcc_app/components/chat_input_field.dart';
import 'package:tcc_app/components/chat_messages.dart';

class ChatbotScreen extends StatelessWidget {
  const ChatbotScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [Expanded(child: ChatMessages()), ChatInputField()],
      ),
    );
  }
}
