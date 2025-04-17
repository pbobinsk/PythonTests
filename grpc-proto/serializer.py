import mydata_pb2 as d

data = d.MyData()
data.id = 123
data.name = "Test Object"
data.items.extend(["itemA", "itemB", "itemC"])
data.values["key1"] = 10
data.values["key2"] = 20

# Serializacja do ciągu bajtów
serialized_data = data.SerializeToString()

print("Zserializowane dane (Python):", serialized_data)

filename = "myDataP.proto.bin"

try:
    with open(filename, "wb") as f:
        f.write(data.SerializeToString())
    print(f"Dane Protobuf zostały zapisane do pliku: {filename}")
except IOError as e:
    print(f"Wystąpił błąd podczas zapisu do pliku: {e}")

# Możesz teraz przesłać te dane (np. przez sieć, zapis do pliku) do Javy