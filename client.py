import xmlrpc.client
from datetime import datetime

def add_XML(server, topic_name, note_name, text):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    response = server.add_or_append_note(topic_name, note_name, text, timestamp)
    return response

def get_XML(server, topic_name):
    notes = server.get_notes_by_topic(topic_name)
    return notes

def wikipedia_information(server, topic_name, note_name):
    response = server.query_wikipedia_and_append(topic_name, note_name)
    return response


def main():
    server = xmlrpc.client.ServerProxy('http://127.0.0.1:8000/')
    while True:
        user_choose = input("Enter add or get or wiki or quit: ").lower()
        
        if user_choose == 'quit':
            print("Exiting")
            break
        
        topic_name = input("Enter topic name: ")
        
        if user_choose == 'add':
            note_name = input("Enter note name: ")
            text = input("Enter text: ")
            if add_XML(server, topic_name, note_name, text):
                print(f"Note '{note_name}' added/updated in topic '{topic_name}'.")
            else:
                print("An error occurred.")
                
        elif user_choose == 'get':
            notes = get_XML(server, topic_name)
            if notes:
                for note in notes:
                    print(f"Note Name: {note['name']}, Text: {note['text']}, Timestamp: {note['timestamp']}")
            else:
                print("No notes found for this topic.")

        elif user_choose == 'wiki':
            note_name = input("Enter Wikipedia search term: ")
            if wikipedia_information(server, topic_name, note_name):
                print(f"Wikipedia information:'{note_name}', topic: '{topic_name}'.")
            else:
                print("An error occurred or no information found.")
                
if __name__ == "__main__":
    main()


