import mydata_pb2 as d

# Symulacja otrzymania zserializowanych danych z Javy
serialized_data_from_java = b'\x08{\x12\x0bTest Object\x1a\x05itemA\x1a\x05itemB\x1a\x05itemC"\x08\n\x04key2\x10\x14"\x08\n\x04key1\x10\n'
data = d.MyData()
data.ParseFromString(serialized_data_from_java)

filename = "myDataJ.proto.bin"
deserialized_data = d.MyData()

try:
    with open(filename, "rb") as f:
        serialized_data = f.read()
        deserialized_data.ParseFromString(serialized_data)

    print("Dane Protobuf zostały odczytane z pliku:")
    print("ID:", deserialized_data.id)
    print("Name:", deserialized_data.name)
    print("Items:", deserialized_data.items)
    print("Values:", deserialized_data.values)

except IOError as e:
    print(f"Wystąpił błąd podczas odczytu z pliku: {e}")

print("Zdeserializowane dane (Python):")
print("ID:", data.id)
print("Name:", data.name)
print("Items:", data.items)
print("Values:", data.values)