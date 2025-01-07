from PIL import Image
import numpy as np

# Tworzymy nowy obraz RGB o wymiarach 100x100, wypełniony kolorem czerwonym
image = Image.new("RGB", (100, 100), color=(255, 0, 0))

# Zapisujemy obraz do pliku
image.save("output_image.png", format="PNG")

# Tworzymy dane obrazu w formie NumPy (100x100, RGB)
data = np.zeros((100, 100, 3), dtype=np.uint8)
data[:, :] = [0, 255, 0]  # Wypełniamy obraz kolorem zielonym

# Tworzymy obiekt Image z danych NumPy
image = Image.fromarray(data)

# Zapisujemy obraz do pliku
image.save("output_image2.png", format="PNG")

# Wczytanie obrazu z pliku
image = Image.open("output_image.png")

# Wyświetlenie podstawowych informacji o obrazie
print(f"Format: {image.format}")
print(f"Rozmiar: {image.size}")
print(f"Tryb kolorów: {image.mode}")

# Opcjonalnie wyświetlenie obrazu w domyślnej przeglądarce graficznej
image.show()

gray_image = image.convert("L")  # Konwersja na skalę szarości
gray_image.save("output_gray.png")

resized_image = image.resize((200, 200))
resized_image.save("resized_image.png")

cropped_image = image.crop((50, 50, 150, 150))  # Wycięcie prostokąta
cropped_image.save("cropped_image.png")