import random

def pika_command(update,context):
    """Sends a pikachu sticker"""
    try:
        if random.random() < 0.01:
            return context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Pika... boo? 🙂"
            )
        pika_list = [
            'pikachu',
            'pikachu2',
            'PikachuDetective',
            'pikachu6',
            'pikach',
            'pikach_memes',
            'PikachyAnim',
            ]
        pikas = []
        for pika in pika_list:
            pikas.extend(context.bot.get_sticker_set(pika).stickers)
        pikas.extend(context.bot.get_sticker_set('uwumon').stickers[:20])
        pika = random.choice(pikas)
        context.bot.send_sticker(
            chat_id=update.effective_chat.id,
            sticker=pika
        )
        print(update.effective_chat.title, update.effective_chat.id, update.message.from_user.username, update.message.from_user.first_name)
    except Exception as e:
        print(e)


def ohno_command(update,context):
    """Sends a version of "Oh no"..."""
    text = random.choice([
        "OH NO!",
        "Oh no indeed...",
        "Oh no",
        "Ah, that is not ideal",
        "This is a pleasant surprise without the pleasant",
        "Goodness gracious me!",
        "Oh noes",
        "Das not good",
        "Aaaaaaaaaaaaaaaaaaaaaaaaaaaaah",
        "How could this happen?!",
        "This calls for an 'Oh no'.",
        "F in the chat",
        "What did you do!?",
        "Seriously...",
        "ono",
        "FSKSJFLKSDJFH",
        "My condolences",
        "Rest in peace good sir",
        "ohhh myyy gawwwd",
        "OMG!",
        "oh no",
        "oh no...?",
        "Bless you",
        "Are you sure you didn't mean 'Oh yes'?",
        "This is truly a disaster",
        "...",
        ])
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text)
