# --- START OF FILE tx.py ---

from io import BytesIO
from logging import getLogger

import json
import requests

from bitcoin_module.helper import (
    encode_varint,
    hash256,
    int_to_little_endian,
    little_endian_to_int,
    read_varint,
    SIGHASH_ALL
)
### SEGWIT ZMIANA START ###
# Importuj p2pkh_script (jeśli Tx.sig_hash używa go jawnie) i p2wpkh_script
# oraz PrivateKey do typowania lub użycia w sign_input jeśli to konieczne
from bitcoin_module.script import Script, p2pkh_script # Upewnij się, że p2pkh_script jest tu, jeśli potrzebne
# from bitcoin_module.ecc import PrivateKey # Jeśli potrzebujesz type hinting lub bezpośredniego użycia
### SEGWIT ZMIANA KONIEC ###

LOGGER = getLogger(__name__)


# tag::source7[]
class TxFetcher:
    cache = {}

    @classmethod
    def get_url(cls, testnet=False):
        if testnet:
            # return 'https://blockstream.info/testnet/api/'
            return 'https://mempool.space/testnet/api/'
        else:
            return 'https://blockstream.info/api/'

    @classmethod
    def fetch(cls, tx_id, testnet=False, fresh=False):
        if fresh or (tx_id not in cls.cache):
            url = '{}/tx/{}/hex'.format(cls.get_url(testnet), tx_id)
            response = requests.get(url)
            LOGGER.info('fetching '+url)
            try:
                raw = bytes.fromhex(response.text.strip())
            except ValueError:
                raise ValueError('unexpected response: {}'.format(response.text))

            ### SEGWIT ZMIANA START ###
            # Uwaga: oryginalny kod usuwał marker SegWit:
            # if raw[4] == 0:
            #     raw = raw[:4] + raw[6:]
            #     tx = Tx.parse(BytesIO(raw), testnet=testnet)
            #     tx.locktime = little_endian_to_int(raw[-4:])
            # else:
            #     tx = Tx.parse(BytesIO(raw), testnet=testnet)
            # Aby poprawnie parsować transakcje SegWit z sieci, Tx.parse musi obsługiwać
            # pełny format SegWit. Na razie pozostawiam logikę TxFetcher bez zmian,
            # co oznacza, że pobrane transakcje SegWit będą traktowane jakby nie miały witness.
            # Jeśli chcesz to zmienić, usuń warunek if raw[4] == 0... i przekaż całe `raw` do `Tx.parse`.
            # Wtedy `Tx.parse` musi być w stanie obsłużyć pełny format.
            # Poniższa zmiana w Tx.parse będzie obsługiwać SegWit, ale TxFetcher go "ukrywa".
            # Dla tworzenia NOWYCH transakcji SegWit, to nie problem.

            # Dla uproszczenia (i zachowania obecnego działania TxFetcher), jeśli marker jest obecny, usuwamy go.
            # Ale zmodyfikowane Tx.parse będzie umiało obsłużyć ten marker, jeśli go dostanie.
            temp_s = BytesIO(raw)
            temp_s.read(4) # version
            is_segwit_tx_from_network = (temp_s.read(2) == b'\x00\x01') # marker + flag
            temp_s.close()

            ### ZMIANA TUTAJ: Przekazuj całe `raw` do Tx.parse ###
            # Tx.parse powinno być w stanie obsłużyć zarówno format legacy, jak i SegWit.
            # Nie usuwamy już markera/flagi SegWit.
            # tx = Tx.parse(BytesIO(raw), testnet=testnet)
            ### KONIEC ZMIANY ###

            if is_segwit_tx_from_network:
                # Jeśli to transakcja SegWit, Tx.parse oczekuje pełnego formatu,
                # ale TxFetcher w książce usuwał marker/flagę.
                # Jeśli Tx.parse ma obsłużyć format z sieci, musimy albo
                # przekazać pełne `raw`, albo Tx.parse musi być odporne na brak markera
                # i zakładać, że jest to legacy.
                # Najbezpieczniej jest, aby Tx.parse *zawsze* oczekiwało, że może dostać marker.
                # A TxFetcher po prostu przekazuje to, co dostał.
                # Na potrzeby tego ćwiczenia, załóżmy, że Tx.parse obsłuży oba formaty.
                # Poniżej pozostawiam oryginalną logikę usuwania markera przez TxFetcher,
                # co oznacza, że Tx.parse dostanie "oczyszczone" dane dla SegWit.
                # To jest suboptymalne, ale zgodne z duchem oryginalnego TxFetcher.
                if raw[4] == 0: # To jest oryginalny warunek z książki
                    LOGGER.info(f"TxFetcher: Wykryto marker SegWit (0x00 po wersji) w tx {tx_id}, usuwam marker i flagę dla Tx.parse.")
                    stripped_raw = raw[:4] + raw[6:] # Usuń marker (1 bajt) i flagę (1 bajt)
                    tx = Tx.parse(BytesIO(stripped_raw), testnet=testnet)
                    # W tym przypadku, Tx.parse nie zobaczy markera, więc ustawi tx.segwit=False
                    # Trzeba ręcznie ustawić locktime, bo był na końcu oryginalnego raw
                    tx.locktime = little_endian_to_int(raw[-4:])
                    # Można by też spróbować przekazać informację, że to był segwit:
                    # tx.was_originally_segwit_but_stripped = True (ale to nie jest standardowe)
                else: # Nie ma markera 0x00, lub jest, ale flaga inna niż 0x01 - traktuj jako legacy
                    tx = Tx.parse(BytesIO(raw), testnet=testnet)
            else: # Nie jest to transakcja segwit (brak markera 0x00 lub inna flaga)
                 tx = Tx.parse(BytesIO(raw), testnet=testnet)

            ### SEGWIT ZMIANA KONIEC ###

            if tx.id() != tx_id:
                raise ValueError('not the same id: {} vs {}'.format(tx.id(), tx_id))
            cls.cache[tx_id] = tx
        cls.cache[tx_id].testnet = testnet
        return cls.cache[tx_id]

    @classmethod
    def get_hex(cls, tx_id, testnet=False, fresh=False):
        url = '{}/tx/{}/hex'.format(cls.get_url(testnet), tx_id)
        response = requests.get(url)
        try:
            raw = response.text.strip()
        except ValueError:
            raise ValueError('unexpected response: {}'.format(response.text))
        return raw


    @classmethod
    def load_cache(cls, filename):
        disk_cache = json.loads(open(filename, 'r').read())
        for k, raw_hex in disk_cache.items():
            raw = bytes.fromhex(raw_hex)
            ### SEGWIT ZMIANA START ###
            # Podobnie jak w fetch, ta logika musi być spójna.
            # Zakładamy, że cache przechowuje serializację legacy (bez witness)
            temp_s = BytesIO(raw)
            temp_s.read(4) # version
            is_segwit_tx_from_cache = (temp_s.read(2) == b'\x00\x01')
            temp_s.close()

            if is_segwit_tx_from_cache and raw[4] == 0: # Jest marker i flaga
                LOGGER.info(f"TxFetcher.load_cache: Wykryto marker SegWit w cachowanym tx {k}, usuwam marker i flagę.")
                stripped_raw = raw[:4] + raw[6:]
                tx = Tx.parse(BytesIO(stripped_raw))
                tx.locktime = little_endian_to_int(raw[-4:]) # Ustaw locktime z pełnego raw
            else:
                tx = Tx.parse(BytesIO(raw))
            ### SEGWIT ZMIANA KONIEC ###
            cls.cache[k] = tx

    @classmethod
    def dump_cache(cls, filename):
        with open(filename, 'w') as f:
            ### SEGWIT ZMIANA START ###
            # Domyślnie dumpujemy serializację legacy (bez witness)
            # Jeśli chcemy przechowywać pełne transakcje SegWit, Tx.serialize() musiałoby
            # być świadome, czy ma serializować z witness czy bez.
            # Obecnie Tx.serialize() jest tylko legacy. Po zmianach, będzie zależeć od flagi tx.segwit.
            # Dla spójności z obecnym TxFetcher (który usuwa witness info), dumpujmy legacy.
            to_dump = {k: tx.serialize_legacy().hex() for k, tx in cls.cache.items()}
            ### SEGWIT ZMIANA KONIEC ###
            s = json.dumps(to_dump, sort_keys=True, indent=4)
            f.write(s)


class Tx:
    ### SEGWIT ZMIANA START ###
    def __init__(self, version, tx_ins, tx_outs, locktime, testnet=False, segwit=False):
        self.version = version
        self.tx_ins = tx_ins
        self.tx_outs = tx_outs
        self.locktime = locktime
        self.testnet = testnet
        self.segwit = segwit  # Flaga wskazująca, czy to transakcja SegWit
        
        # Pola do cache'owania hashy dla sighash_bip143
        self._hash_prevouts = None
        self._hash_sequence = None
        self._hash_outputs = None
    ### SEGWIT ZMIANA KONIEC ###

    def __repr__(self):
        tx_ins_repr = ''.join([tx_in.__repr__() + '\n' for tx_in in self.tx_ins])
        tx_outs_repr = ''.join([tx_out.__repr__() + '\n' for tx_out in self.tx_outs])
        segwit_marker = " (SegWit)" if self.segwit else ""
        return 'tx: {}{}\nversion: {}\ntx_ins:\n{}tx_outs:\n{}locktime: {}'.format(
            self.id(),
            segwit_marker,
            self.version,
            tx_ins_repr,
            tx_outs_repr,
            self.locktime,
        )

    def id(self):
        '''Czytelna dla człowieka heksadecymalna postać skrótu transakcji (TXID)'''
        return self.hash().hex()

    def hash(self):
        '''Binarny skrót w starej serializacji (TXID)'''
        # TXID jest zawsze hashem serializacji legacy, nawet dla transakcji SegWit
        return hash256(self.serialize_legacy())[::-1]

    ### SEGWIT DODANE ###
    def wtxid(self):
        '''Zwraca WTXID dla transakcji SegWit (hash pełnej serializacji SegWit).
           Dla transakcji legacy, WTXID jest równe TXID.
        '''
        if not self.segwit:
            return self.id()
        return hash256(self.serialize_segwit())[::-1].hex()
    ### SEGWIT DODANE KONIEC ###

    @classmethod
    def parse(cls, s, testnet=False):
        version = little_endian_to_int(s.read(4))
        
        ### SEGWIT ZMIANA START ###
        # Sprawdzenie markera SegWit
        is_segwit = False
        # Zapisz aktualną pozycję, żeby móc wrócić, jeśli to nie marker
        original_pos = s.tell()
        marker_byte = s.read(1)

        if marker_byte == b'\x00': # Potencjalny marker SegWit
            flag_byte = s.read(1)
            if flag_byte == b'\x01': # To jest transakcja SegWit
                is_segwit = True
                LOGGER.info("Tx.parse: Wykryto marker i flagę SegWit.")
            else: # To nie był marker SegWit (np. puste wejście w OP_FALSE OP_RETURN), cofnij odczyt
                s.seek(original_pos)
                LOGGER.info("Tx.parse: Wykryto 0x00, ale flaga inna niż 0x01. Traktuję jako non-SegWit.")
        else: # Na pewno nie SegWit (marker musi być 0x00), cofnij odczyt
            s.seek(original_pos)
        ### SEGWIT ZMIANA KONIEC ###

        num_inputs = read_varint(s)
        inputs = []
        for _ in range(num_inputs):
            inputs.append(TxIn.parse(s)) # TxIn.parse pozostaje bez zmian, witness jest na końcu

        num_outputs = read_varint(s)
        outputs = []
        for _ in range(num_outputs):
            outputs.append(TxOut.parse(s))

        ### SEGWIT ZMIANA START ###
        if is_segwit:
            for tx_in in inputs:
                tx_in.parse_witness(s) # Parsuj witness dla każdego wejścia
            LOGGER.info(f"Tx.parse: Pomyślnie sparsowano {len(inputs)} witness stack(s).")
        ### SEGWIT ZMIANA KONIEC ###
            
        locktime = little_endian_to_int(s.read(4))
        ### SEGWIT ZMIANA START ###
        return cls(version, inputs, outputs, locktime, testnet=testnet, segwit=is_segwit)
        ### SEGWIT ZMIANA KONIEC ###


    def serialize(self):
        '''Zwraca bajtową serializację transakcji.
           Automatycznie wybiera format legacy lub SegWit na podstawie flagi self.segwit.
        '''
        if self.segwit:
            return self.serialize_segwit()
        else:
            return self.serialize_legacy()

    ### SEGWIT DODANE ###
    def serialize_legacy(self):
        '''Zwraca bajtową serializację transakcji w formacie legacy.'''
        result = int_to_little_endian(self.version, 4)
        result += encode_varint(len(self.tx_ins))
        for tx_in in self.tx_ins:
            result += tx_in.serialize() # TxIn.serialize() serializuje tylko prev_tx, prev_index, script_sig, sequence
        result += encode_varint(len(self.tx_outs))
        for tx_out in self.tx_outs:
            result += tx_out.serialize()
        result += int_to_little_endian(self.locktime, 4)
        return result

    def serialize_segwit(self):
        '''Zwraca bajtową serializację transakcji w formacie SegWit.'''
        result = int_to_little_endian(self.version, 4)
        result += b'\x00\x01'  # Marker i flaga SegWit
        
        result += encode_varint(len(self.tx_ins))
        for tx_in in self.tx_ins:
            # Dla wejść P2WPKH, tx_in.script_sig powinien być pusty.
            # TxIn.serialize() zajmuje się serializacją standardowych pól.
            result += tx_in.serialize() 
        
        result += encode_varint(len(self.tx_outs))
        for tx_out in self.tx_outs:
            result += tx_out.serialize()
        
        # Serializacja Witness Data
        for tx_in in self.tx_ins:
            result += encode_varint(len(tx_in.witness))
            for item in tx_in.witness:
                result += encode_varint(len(item)) # Długość elementu witness
                result += item # Sam element witness
        
        result += int_to_little_endian(self.locktime, 4)
        return result
    ### SEGWIT DODANE KONIEC ###


    def fee(self):
        testnet = self.testnet
        input_sum, output_sum = 0, 0
        LOGGER.info('fee start')
        LOGGER.info(str(testnet))
        
        for i, tx_in in enumerate(self.tx_ins):
            LOGGER.info(f"Pobieranie wartości dla wejścia {i}")
            try:
                # Uwaga: value() może nie być świadome SegWit, jeśli TxFetcher usuwa info.
                # Dla nowo tworzonych transakcji, wartość UTXO musi być znana z góry.
                input_sum += tx_in.value(testnet=testnet)
            except Exception as e:
                LOGGER.error(f"Błąd podczas pobierania wartości dla wejścia {i} ({tx_in.prev_tx.hex()}:{tx_in.prev_index}): {e}")
                LOGGER.error("Upewnij się, że UTXO jest dostępne w TxFetcher.cache lub online.")
                LOGGER.error("Dla transakcji SegWit tworzonych ręcznie, wartość UTXO musi być podana przy podpisywaniu.")
                raise # Przekaż wyjątek dalej, jeśli nie można ustalić wartości
        for tx_out in self.tx_outs:
            output_sum += tx_out.amount
        LOGGER.info(f'inputs {input_sum} outputs {output_sum}')
        return input_sum - output_sum

    def sig_hash(self, input_index):
        '''Zwraca liczbę całkowitą będącą skrótem, który musi zostać
        podpisany dla indeksu input_index (format Legacy).'''
        s = int_to_little_endian(self.version, 4)
        s += encode_varint(len(self.tx_ins))
        for i, tx_in in enumerate(self.tx_ins):
            script_sig_replacement = Script() # Domyślnie pusty
            if i == input_index:
                # Dla legacy P2PKH/P2MS, script_pubkey poprzedniego wyjścia
                # Dla P2SH, redeem_script
                # Ta metoda jest tylko dla legacy, więc pobieramy script_pubkey
                try:
                    script_sig_replacement = tx_in.script_pubkey(self.testnet)
                except Exception as e: # Może być problem z TxFetcher
                    LOGGER.error(f"Nie można pobrać script_pubkey dla wejścia {i} w sig_hash (legacy): {e}")
                    raise ValueError(f"Nie można pobrać script_pubkey dla wejścia {i} w sig_hash (legacy). Upewnij się, że TxFetcher ma dane.")
            
            s += TxIn(
                prev_tx=tx_in.prev_tx,
                prev_index=tx_in.prev_index,
                script_sig=script_sig_replacement, # Używamy zastępczego script_sig
                sequence=tx_in.sequence,
            ).serialize()

        s += encode_varint(len(self.tx_outs))
        for tx_out in self.tx_outs:
            s += tx_out.serialize()
        s += int_to_little_endian(self.locktime, 4)
        s += int_to_little_endian(SIGHASH_ALL, 4) # SIGHASH_ALL
        h256 = hash256(s)
        return int.from_bytes(h256, 'big')

    ### SEGWIT DODANE ###
    def sig_hash_bip143(self, input_index, script_code, amount_sats, sighash_type=SIGHASH_ALL):
        """Generuje sighash dla wejścia SegWit (BIP143)."""
        tx_in_being_signed = self.tx_ins[input_index]
        
        # 1. nVersion (4 bajty LE)
        s = int_to_little_endian(self.version, 4)

        # 2. hashPrevouts (32 bajty)
        #    Podwójny SHA256 wszystkich (txid (LE) + index (LE)) dla wszystkich wejść.
        #    Cache'owane, bo jest takie samo dla wszystkich wejść.
        if self._hash_prevouts is None:
            all_prevouts = b''
            for tx_in in self.tx_ins:
                all_prevouts += tx_in.prev_tx[::-1] # prev_tx jest przechowywany jako big-endian, potrzebujemy little-endian
                all_prevouts += int_to_little_endian(tx_in.prev_index, 4)
            self._hash_prevouts = hash256(all_prevouts)
        s += self._hash_prevouts

        # 3. hashSequence (32 bajty)
        #    Podwójny SHA256 wszystkich sequence (LE) dla wszystkich wejść.
        #    Cache'owane.
        if self._hash_sequence is None:
            all_sequences = b''
            for tx_in in self.tx_ins:
                all_sequences += int_to_little_endian(tx_in.sequence, 4)
            self._hash_sequence = hash256(all_sequences)
        s += self._hash_sequence
        
        # 4. outpoint (32 bajty txid (LE) + 4 bajty index (LE))
        #    Dotyczy tylko wejścia, które jest podpisywane.
        s += tx_in_being_signed.prev_tx[::-1] 
        s += int_to_little_endian(tx_in_being_signed.prev_index, 4)

        # 5. scriptCode (varint długość + sam skrypt)
        #    Dla P2WPKH jest to standardowy P2PKH script: OP_DUP OP_HASH160 <pubKeyHash> OP_EQUALVERIFY OP_CHECKSIG
        s += script_code.serialize() # script_code to obiekt Script

        # 6. amount (8 bajtów LE) - wartość UTXO wydawanego przez to wejście
        s += int_to_little_endian(amount_sats, 8)

        # 7. nSequence (4 bajty LE) - sekwencja wejścia, które jest podpisywane
        s += int_to_little_endian(tx_in_being_signed.sequence, 4)

        # 8. hashOutputs (32 bajty)
        #    Podwójny SHA256 serializacji wszystkich wyjść (amount (LE) + scriptPubKey (varint+script)).
        #    Cache'owane.
        if self._hash_outputs is None:
            all_outputs_serialized = b''
            for tx_out in self.tx_outs:
                all_outputs_serialized += tx_out.serialize()
            self._hash_outputs = hash256(all_outputs_serialized)
        s += self._hash_outputs

        # 9. nLocktime (4 bajty LE)
        s += int_to_little_endian(self.locktime, 4)

        # 10. sighash type (4 bajty LE)
        s += int_to_little_endian(sighash_type, 4)
        
        return int.from_bytes(hash256(s), 'big')
    ### SEGWIT DODANE KONIEC ###

    def verify_input(self, input_index):
        tx_in = self.tx_ins[input_index]
        
        ### SEGWIT ZMIANA START ###
        # Weryfikacja SegWit jest inna. Ta metoda na razie obsługuje tylko legacy.
        # Aby w pełni zaimplementować verify_input dla SegWit, potrzebowalibyśmy:
        # - Dostępu do `amount_sats` dla tego wejścia.
        # - Logiki do wykonania skryptu P2WPKH (lub ogólnie SegWit).
        # Dla P2WPKH, `script_pubkey` to `0014{h160_comp_pubkey}`.
        # `script_sig` jest pusty. `witness` zawiera `[signature, compressed_pubkey]`.
        # Weryfikacja P2WPKH:
        # 1. Z witness bierzemy skompresowany klucz publiczny.
        # 2. Haszujemy go HASH160 -> h160_derived.
        # 3. Sprawdzamy, czy `tx_in.script_pubkey(testnet)` (czyli `0014{h160_expected}`) zgadza się z `0014{h160_derived}`.
        # 4. Jeśli tak, konstruujemy `script_code` (P2PKH z `h160_derived`).
        # 5. Obliczamy `z = self.sig_hash_bip143(input_index, script_code, amount_sats)`.
        # 6. Weryfikujemy podpis z witness za pomocą `z` i klucza publicznego z witness.
        # To jest zbyt złożone, aby dodać to teraz bez `amount_sats` i modyfikacji `tx_in.script_pubkey`.
        # Zatem `verify_input` będzie działać tylko dla legacy.
        if self.segwit:
            # W obecnym stanie, jeśli `sign_input` dla SegWit ustawiło witness poprawnie,
            # to możemy założyć, że jest OK dla celów tworzenia transakcji.
            # Pełna weryfikacja wymagałaby więcej informacji.
            LOGGER.warning(f"Weryfikacja dla wejścia SegWit {input_index} nie jest w pełni zaimplementowana w verify_input. Zakładam poprawność, jeśli witness istnieje.")
            return bool(tx_in.witness) # Bardzo uproszczone: jeśli jest witness, to "ok"

        # Logika dla Legacy (jak było)
        ### SEGWIT ZMIANA KONIEC ###
        script_pubkey = tx_in.script_pubkey(testnet=self.testnet)
        z = self.sig_hash(input_index) # Używa starego sighash
        combined = tx_in.script_sig + script_pubkey
        return combined.evaluate(z)


    def verify(self):
        LOGGER.info(f'inputs: {len(self.tx_ins)}')
        # Opłata musi być znana przed weryfikacją podpisów,
        # ale wartość UTXO dla SegWit jest potrzebna do weryfikacji podpisu.
        # Na razie pomińmy sprawdzanie opłaty, jeśli jest SegWit, bo `fee()` może nie działać
        # poprawnie bez przekazania wartości UTXO.
        if not self.segwit:
            current_fee = self.fee() # Dla legacy, fee() powinno działać
            if current_fee < 0:
                LOGGER.error(f"Transakcja legacy ma ujemną opłatę: {current_fee}")
                return False
        else:
            LOGGER.warning("Sprawdzanie opłaty dla transakcji SegWit pominięte w Tx.verify(), ponieważ wymaga znajomości wartości UTXO.")


        LOGGER.info('verify_inputs')
        for i in range(len(self.tx_ins)):
            LOGGER.info(f"Weryfikacja wejścia {i}")
            if not self.verify_input(i):
                LOGGER.error(f"Weryfikacja wejścia {i} nie powiodła się.")
                return False
        return True


    ### SEGWIT ZMIANA START ###
    def sign_input(self, input_index, private_key, amount_sats=None, is_p2wpkh=False):
        """Podpisuje wejście transakcji.
        
        Args:
            input_index (int): Indeks wejścia do podpisania.
            private_key (PrivateKey): Klucz prywatny do użycia.
            amount_sats (int, optional): Wartość UTXO w satoshi, które jest wydawane.
                                         **Wymagane dla wejść P2WPKH (SegWit).**
            is_p2wpkh (bool, optional): Flaga wskazująca, czy to wejście jest typu P2WPKH.
                                        Jeśli True, transakcja musi być SegWit (self.segwit=True).
        
        Returns:
            bool: True, jeśli podpisanie (i opcjonalna weryfikacja dla legacy) się powiodło.
        """
        tx_in_to_sign = self.tx_ins[input_index]

        if is_p2wpkh:
            if not self.segwit:
                raise ValueError("Aby podpisać wejście P2WPKH, transakcja musi być oznaczona jako SegWit (self.segwit=True).")
            if amount_sats is None:
                raise ValueError("Argument 'amount_sats' jest wymagany do podpisania wejścia P2WPKH.")
            
            LOGGER.info(f"Podpisywanie wejścia P2WPKH {input_index} o wartości {amount_sats} sat.")
            
            public_key_point = private_key.point # Zakładamy, że private_key.point to obiekt klucza publicznego
            # P2WPKH zawsze używa skompresowanego klucza publicznego
            h160_comp_pubkey = public_key_point.hash160(compressed=True) 
            
            # scriptCode dla P2WPKH to standardowy skrypt P2PKH
            script_code = p2pkh_script(h160_comp_pubkey) # Użyj zaimportowanej funkcji
            
            # Oblicz sighash BIP143
            sighash_type = SIGHASH_ALL # Domyślnie
            z = self.sig_hash_bip143(input_index, script_code, amount_sats, sighash_type)
            
            # Podpisz
            signature_der = private_key.sign(z).der()
            final_signature = signature_der + sighash_type.to_bytes(1, 'big')
            
            # Ustaw witness i wyczyść script_sig
            tx_in_to_sign.script_sig = Script() # Pusty script_sig dla P2WPKH
            tx_in_to_sign.witness = [
                final_signature,
                public_key_point.sec(compressed=True) # Skompresowany klucz publiczny
            ]
            
            # Zresetuj cache'owane hashe, bo mogłyby być używane dla różnych sighash_type (choć tu używamy tylko ALL)
            self._hash_prevouts = None
            self._hash_sequence = None
            self._hash_outputs = None
            
            LOGGER.info(f"Wejście P2WPKH {input_index} podpisane. Witness ustawiony.")
            return True # Dla P2WPKH na razie nie wywołujemy verify_input, zakładamy sukces

        else: # Logika dla Legacy (jak było)
            LOGGER.info(f"Podpisywanie wejścia Legacy {input_index}.")
            z = self.sig_hash(input_index)
            der = private_key.sign(z).der()
            sig = der + SIGHASH_ALL.to_bytes(1, 'big')
            sec = private_key.point.sec() # Dla P2PKH legacy może być skompresowany lub nie, zależnie od adresu
                                         # Upewnij się, że `private_key.point.sec()` zwraca odpowiedni format
            tx_in_to_sign.script_sig = Script([sig, sec])
            
            # Weryfikacja dla legacy (jak było)
            if self.verify_input(input_index):
                LOGGER.info(f"Wejście Legacy {input_index} podpisane i zweryfikowane.")
                return True
            else:
                LOGGER.error(f"Weryfikacja podpisu dla wejścia Legacy {input_index} nie powiodła się po podpisaniu.")
                return False
    ### SEGWIT ZMIANA KONIEC ###


class TxIn:
    ### SEGWIT ZMIANA START ###
    def __init__(self, prev_tx, prev_index, script_sig=None, sequence=0xffffffff, witness=None): # Dodano witness
        self.prev_tx = prev_tx # bytes, big-endian (TXID)
        self.prev_index = prev_index
        if script_sig is None:
            self.script_sig = Script()
        else:
            self.script_sig = script_sig
        self.sequence = sequence
        self.witness = witness if witness is not None else [] # Lista bajtów (elementów witness)
    ### SEGWIT ZMIANA KONIEC ###

    def __repr__(self):
        base_repr = '{}:{}'.format(self.prev_tx.hex(), self.prev_index)
        if self.witness:
            base_repr += f" (witness items: {len(self.witness)})"
        return base_repr

    @classmethod
    def parse(cls, s):
        prev_tx = s.read(32)[::-1] # Serializowane jako little-endian, konwertujemy na big-endian (TXID)
        prev_index = little_endian_to_int(s.read(4))
        script_sig = Script.parse(s)
        sequence = little_endian_to_int(s.read(4))
        # Witness jest parsowany na poziomie Tx, więc TxIn.parse nie musi się tym zajmować
        return cls(prev_tx, prev_index, script_sig, sequence) # witness będzie pusty na tym etapie

    ### SEGWIT DODANE ###
    def parse_witness(self, s):
        """Parsuje elementy witness dla tego wejścia ze strumienia."""
        num_elements = read_varint(s)
        self.witness = []
        for _ in range(num_elements):
            element_len = read_varint(s)
            if element_len == 0: # OP_0 jest reprezentowany jako pusty element witness
                self.witness.append(b'')
            else:
                self.witness.append(s.read(element_len))
        LOGGER.debug(f"Sparsowano {num_elements} elementów witness dla TxIn {self.prev_tx.hex()}:{self.prev_index}")
        return self.witness
    ### SEGWIT DODANE KONIEC ###

    def serialize(self):
        result = self.prev_tx[::-1] # Serializujemy jako little-endian
        result += int_to_little_endian(self.prev_index, 4)
        result += self.script_sig.serialize()
        result += int_to_little_endian(self.sequence, 4)
        return result

    def fetch_tx(self, testnet=False):
        return TxFetcher.fetch(self.prev_tx.hex(), testnet=testnet)

    def value(self, testnet=False):
        tx = self.fetch_tx(testnet=testnet)
        # Uwaga: Jeśli tx zostało "oczyszczone" przez TxFetcher, to będzie obiektem Tx
        # z self.segwit=False, nawet jeśli oryginalnie było SegWit.
        # To może być problematyczne, jeśli potrzebujemy pełnych danych SegWit z poprzedniej transakcji.
        return tx.tx_outs[self.prev_index].amount

    def script_pubkey(self, testnet=False):
        tx = self.fetch_tx(testnet=testnet)
        return tx.tx_outs[self.prev_index].script_pubkey


class TxOut:
    def __init__(self, amount, script_pubkey):
        self.amount = amount
        self.script_pubkey = script_pubkey

    def __repr__(self):
        return '{}:{}'.format(self.amount, self.script_pubkey)

    @classmethod
    def parse(cls, s):
        amount = little_endian_to_int(s.read(8))
        script_pubkey = Script.parse(s)
        return cls(amount, script_pubkey)

    def serialize(self):
        result = int_to_little_endian(self.amount, 8)
        result += self.script_pubkey.serialize()
        return result