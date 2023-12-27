import UniversalSpeech

# Create an instance of UniversalSpeech
uspeech = UniversalSpeech.UniversalSpeech()

# Enable the use of native speech engines such as SAPI 
uspeech.enable_native_speech(True)

#Say a message
uspeech.say("Hello, world.")

# Display a message in braille
uspeech.braille("Hello, world.")

# Get engine used
engine_used = uspeech.engine_used
print("You are using {}.".format(engine_used))

# Get list of available engins
available_engines = uspeech.get_engines()
print(available_engines)

# set the rate if it is supported
try:
    uspeech.set_rate(150)
except UniversalSpeech.exceptions.UnsupportedError as e:
    print(e)

