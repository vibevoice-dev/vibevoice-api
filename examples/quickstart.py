        """Minimal VibeVoice example: create one prediction and print the output URL(s)."""
        import vibevoice_api

        output = vibevoice_api.run({
    "text": "Hello, this is a test of MiMo speech synthesis."
})
        print(output)
