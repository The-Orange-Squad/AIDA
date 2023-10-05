import json
import os

class AIDA_Modification():
    def __init__ (self, id, definition, name, author):
        self.id = id
        self.definition = definition
        self.name = name
        self.author = author
    def save(self):
        # Save the modification to a file.
        # The chatbot will be stored in a file directory called "chatbots". Each file there will be named after the chatbot ID, and will contain the chatbot's data (JSON).
        # The file will be named after the ID.

        # Create the file.
        file = open('modifications/' + self.id + '.json', 'w')
        with file:
            # Write the data.
            file.write(json.dumps(self.__dict__))
    def delete(self):
        # Delete the modification.
        os.remove('modifications/' + self.id + '.json')
    def edit(self, definition, name, author):
        # Edit the modification.
        self.definition = definition
        self.name = name
        self.author = author
        self.save()
    

def load():
    modifications = []
    for file in os.listdir('modifications'):
        if not file.endswith('.json'):
            continue
        # Load the file.
        file = open('modifications/' + file, 'r')
        with file:
            # Load the data.
            data = json.loads(file.read())
            # Create the modification.
            modification = AIDA_Modification(data['id'], data['definition'], data['name'], data['author'])
            # Add the modification to the list.
            modifications.append(modification)
    return modifications