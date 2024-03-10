from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from socketserver import ThreadingMixIn
import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString
from datetime import datetime
import threading
import os
import requests

def prettify_xml(elem):
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="    ")
    pretty_xml_lines = pretty_xml.splitlines()
    non_empty_lines = [line for line in pretty_xml_lines if line.strip()]
    return '\n'.join(non_empty_lines)

class ThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass

class NotesServer:
    def __init__(self, db_path):
        self.db_path = db_path
        self.lock = threading.Lock()
        if not os.path.exists(db_path):
            root = ET.Element("data")
            tree = ET.ElementTree(root)
            with open(db_path, "wb") as f:
                f.write(prettify_xml(root).encode('utf-8'))

    def add_or_append_note(self, topic_name, note_name, text, timestamp):
        with self.lock:
            try:
                tree = ET.parse(self.db_path)
                root = tree.getroot()
                topic = root.find(f".//topic[@name='{topic_name}']")
                if topic is None:
                    topic = ET.SubElement(root, 'topic', attrib={'name': topic_name})
                note = ET.SubElement(topic, 'note', attrib={'name': note_name})
                ET.SubElement(note, 'text').text = text
                ET.SubElement(note, 'timestamp').text = timestamp
                with open(self.db_path, "wb") as f:
                    f.write(prettify_xml(root).encode('utf-8'))
                return True
            except ET.ParseError:
                print(f"Error in XML file: {self.db_path}")
            except Exception as e:
                print(f"Error occurred when adding: {e}")
            return False


    def get_notes_by_topic(self, topic_name):
        tree = ET.parse(self.db_path)
        root = tree.getroot()
        topic = root.find(f".//topic[@name='{topic_name}']")
        notes = []
        if topic is not None:
            for note in topic.findall('note'):
                notes_info = {
                    'name': note.get('name'),
                    'text': note.find('text').text.strip(),
                    'timestamp': note.find('timestamp').text.strip()
                }
                notes.append(notes_info)
        return notes
    
    def query_wikipedia_and_append(self, topic_name, search_term):
        url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + search_term
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            title = data.get("title")
            extract = data.get("extract")
            wiki_url = data.get("content_urls", {}).get("desktop", {}).get("page")
            if not title or not wiki_url:
                return False
            text = (
                f"Wikipedia article: {title}\n"
                f"            Data information: {extract}\n"
                f"            URL: {wiki_url}"
            )
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return self.add_or_append_note(topic_name, search_term, text, timestamp)
        except requests.RequestException as e:
            print(f"Failed in Wikipedia: {e}")
            return False


def main():
    server = ThreadedXMLRPCServer(('localhost', 8000), allow_none=True)
    db_path = 'db1.xml'
    server.register_instance(NotesServer(db_path))
    print("Multithreaded Server Running.")
    server.serve_forever()

if __name__ == "__main__":
    main()


