def test_command(update,context):
    print(context)
    context.bot.send_message(
        text=f'Testing: chat id: {update.message.chat.id}',
        chat_id=update.effective_chat.id
    )
    