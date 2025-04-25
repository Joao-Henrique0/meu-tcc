import 'package:flutter/material.dart';

class ChatInputField extends StatelessWidget {
  final TextEditingController _controller = TextEditingController();

  ChatInputField({super.key});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.all(8.0),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: _controller,
              decoration: InputDecoration(
                hintText: "Digite uma mensagem...",
                hintStyle: Theme.of(context).textTheme.bodyLarge,
                filled: true,
                fillColor:
                    Theme.of(
                      context,
                    ).colorScheme.tertiary, // Fundo levemente acinzentado
                contentPadding: EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 12,
                ),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(
                    25,
                  ), // Bordas arredondadas
                  borderSide: BorderSide.none, // Remove a borda padrão
                ),
                suffixIcon: IconButton(
                  icon: Icon(
                    Icons.send,
                    color: Theme.of(context).colorScheme.secondary,
                  ),
                  onPressed: () {
                    print("Mensagem enviada: ${_controller.text}");
                    _controller.clear();
                  },
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
