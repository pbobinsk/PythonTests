const { createApp, ref, onMounted } = Vue;

createApp({
  setup() {
    const fact = ref('');
    const source = ref('');
    const timestamp = ref('');
    const loading = ref(false);
    const error = ref('');
    const CACHE_EXPIRATION_SECONDS = 10; // Taka sama wartość jak w backendzie dla informacji

    const fetchFact = async () => {
      loading.value = true;
      error.value = '';
      try {
        // Ważne: Używamy pełnego URL, ponieważ frontend i backend działają na różnych portach
        // W docker-compose, frontend może odwoływać się do `http://flask_app:5000/api/fact`
        // Ale przeglądarka użytkownika odwołuje się do `http://localhost:5000/api/fact`
        const response = await fetch('http://localhost:5000/api/fact');
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        fact.value = data.fact;
        source.value = data.source;
        timestamp.value = new Date(data.timestamp * 1000).toLocaleTimeString();

      } catch (e) {
        console.error("Błąd pobierania faktu:", e);
        error.value = `Nie można pobrać faktu: ${e.message}`;
        fact.value = ''; // Wyczyść stary fakt w razie błędu
        source.value = '';
        timestamp.value = '';
      } finally {
        loading.value = false;
      }
    };

    onMounted(fetchFact); // Pobierz fakt przy załadowaniu strony

    return {
      fact,
      source,
      timestamp,
      loading,
      error,
      fetchFact,
      CACHE_EXPIRATION_SECONDS
    };
  }
}).mount('#app');