def to_binary(a, size):
    binary = [int(x) for x in list('{0:0b}'.format(a))]
    while len(binary) < size:
        binary.insert(0,0)
    return binary

def chunks(lst, n): # découpe une liste en morceau de taille n
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def left_rotate(x, c):
    x &= 0xffffffff
    return ((x << c) | (x >> (32 - c))) & 0xffffffff


def ascii_to_binary_list(message):
    binary_list = []    
    for char in message:
        binary_list+=(to_binary(ord(char),8))
    return binary_list

def bytes_to_binary_list(bytes):
    bytes_as_bits = ''.join(format(byte, '08b') for byte in bytes)
    list = [] 
    for bit in bytes_as_bits:
            list.append(int(bit))
    return list

def padding(bits): # on ajoute '1' puis des '0' jusquà obtenir une longueur congru à 448 mod 512
    bits.append(1)
    while ((len(bits) % 512) != 448):
        bits.append(0)
    return bits

def message_length_on_64_bits(length):
    message_length_bits = to_binary(length & 0xffffffffffffffff, 64)
    return message_length_bits

def chunker(bits, chunk_length=32): # pas codé par moi
    # divides list of bits into desired byte/word chunks, 
    # starting at LSB 
    chunked = []
    for b in range(0, len(bits), chunk_length):
        chunked.append(bits[b:b+chunk_length])
    return chunked

def chunks(bits):
    M = [bits[i:i + 512] for i in range(0, len(bits), 512)]
    length = len(M)
    for n in range(length):
        M[n] = chunker(M[n]) 
    return M

def binary_to_int(binary): # pas codé par moi
    return sum(val*(2**idx) for idx, val in enumerate(reversed(binary)))

def chunks_to_int(bits): 
    numberOf512bitsChunks = len(bits)
    for i in range(numberOf512bitsChunks):
        for j in range(16):
            bits[i][j] = binary_to_int(bits[i][j])
    return bits

def extendChunkTo80(chunk):
    chunk+=([0]*64)
    return chunk

def sha1(bytes):
    # coonstantes 
 
    h0 = 0x67452301
    h1 = 0xEFCDAB89
    h2 = 0x98BADCFE
    h3 = 0x10325476
    h4 = 0xC3D2E1F0

    """1/ préparation"""

    bits = bytes_to_binary_list(bytes)

    length = len(bits)

    #print("message as binary list :",bits)

    bits = padding(bits)
    

    #print("\n")

    #print("message padded :",bits)

    bits+=message_length_on_64_bits(length)

  

    #print("\n")

    #print("message padded with message length added:",bits)


    """2/ 512 bits chunks puis 32 bits chunks"""

    M = chunks(bits)

    #print("\n")

    #print("bits chunked:",M)

    """3/ converting 32bits list to int"""

    M = chunks_to_int(M)
        
    #print("\n")

    #print("32 bits list to Int:",M)

    """4/ etendre les 16 chunks à 80 chunk"""

    for chunk in M:

        """5/ on étend les 16 chunks de 32 bits à 80 chunks de 32 bits"""

        chunk = extendChunkTo80(chunk)

        #print("\n")

        #print("extended chunk:",M)

        """6/ on mélange les chunks entre eux"""

        for i in range(16,80):
            chunk[i] = left_rotate(chunk[i-3] ^ chunk[i-8] ^ chunk[i-14] ^ chunk[i-16], 1)
        
        #print("\n")

        #print("mixed chunk:",M)

        a = h0
        b = h1
        c = h2
        d = h3
        e = h4


        for i in range (80):
            
            if 0 <= i <= 19 :
                f = ((b & c) | ((~b) & d)) 
                k = 0x5A827999
            elif (20 <= i <= 39):
                f = (b ^ c ^ d) 
                k = 0x6ED9EBA1
            elif 40 <= i <= 59:
                f = (((b & c) | (b & d) | (c & d) ) ) 
                k = 0x8F1BBCDC
            elif 60 <= i <= 79:
                f = (b ^ c ^ d) 
                k = 0xCA62C1D6

            temp = left_rotate(a,5) + f + e + k + chunk[i] 
            e = d
            d = c
            c = left_rotate(b,30) 
            b = a
            a = temp

        h0 = (h0 + a) & 0xffffffff
        h1 = (h1 + b) & 0xffffffff
        h2 = (h2 + c) & 0xffffffff
        h3 = (h3 + d) & 0xffffffff
        h4 = (h4 + e) & 0xffffffff

        

    """8/ final"""
    hh = (h0 << 128)  | ( h1 << 96)  | (h2 << 64)  | (h3 << 32)  | h4 


    return(hh.to_bytes(20, 'big'))


def to_hex(bytes):
    return hex(int.from_bytes(bytes, 'big') )
