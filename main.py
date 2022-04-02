from bot import updater

if __name__ == "__main__":
    # main()
    try:
        updater.start_polling()
        updater.idle()
    except Exception as e:
        print(e)
