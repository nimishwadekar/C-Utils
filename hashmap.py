import sys

n = len(sys.argv)
if n != 3 and n != 4:
    print('Enter command line arguments in this format:')
    print('<Key Type> <Value Type> [<Map Name>]')
    exit()

keyt = sys.argv[1]
keyiden = keyt.replace('*', '_ptr')
keyempty = keyiden.upper()
valt = sys.argv[2]
validen = valt.replace('*', '_ptr')
hmap = f'Map_{keyiden}_{validen}' if n == 3 else sys.argv[3]
include_guard = hmap.upper() + '_H'


header = f"""#ifndef {include_guard}
#define {include_guard}

typedef struct {hmap} {hmap};

const {keyt} EMPTY_{keyempty}_KEY = 0;

// Dynamically allocates a {hmap} and returns a pointer to it.
{hmap}* {hmap}_create(void);

// Inserts a key and its associated value into the {hmap}.
void {hmap}_insert({hmap}* map, {keyt} key, {valt} value);

// Gets the value associated with the key from the {hmap}, if present. If not, returns a value denoting an empty key.
{valt} {hmap}_get({hmap}* map, {keyt} key);

// Removes the key from the {hmap}, if present.
void {hmap}_remove({hmap}* map, {keyt} key);

// Deallocates the {hmap} from memory.
void {hmap}_free({hmap}* map);

#endif"""


code = f"""#include <stddef.h>
#include <stdbool.h>
#include <stdlib.h>
#include "{hmap}.h"

#define loadFactor 0.8

typedef struct
{{
    {keyt} key;
    {valt} value;
    size_t offset;
}} Entry;

struct {hmap}
{{
    Entry* entries;
    size_t count, capacity;
    
    bool emptyKeyPresent;
    {valt} emptyKeyValue;
}};

size_t hash({keyt} key)
{{
    return key;
}}

{hmap}* {hmap}_create(void)
{{
    {hmap}* map = ({hmap}*) malloc(sizeof({hmap}));
    map->count = 0;
    map->capacity = 16;
    map->entries = (Entry*) malloc(16 * sizeof(Entry));
    for(size_t i = 0; i < 16; i++) map->entries[i].key = EMPTY_{keyempty}_KEY;
    map->emptyKeyPresent = false;
    return map;
}}

void {hmap}_insert({hmap}* map, {keyt} key, {valt} value)
{{
    if(key == EMPTY_{keyempty}_KEY)
    {{
        map->emptyKeyPresent = true;
        map->emptyKeyValue = value;
        return;
    }}
    
    size_t count = map->count, capacity = map->capacity;
    if(count > (size_t) (capacity * loadFactor))
    {{
        map->capacity <<= 1;
        map->count = 0;
        Entry* oldEntries = map->entries;
        map->entries = (Entry*) malloc(map->capacity * sizeof(Entry));
        for(size_t i = 0; i < map->capacity; i++) map->entries[i].key = EMPTY_{keyempty}_KEY;
        
        for(size_t i = 0; i < capacity; i++)
        {{
            if(oldEntries[i].key != EMPTY_{keyempty}_KEY)
            {{
                {hmap}_Put(map, oldEntries[i].key, oldEntries[i].value);
            }}
        }}
        capacity = map->capacity;
        free(oldEntries);
    }}
    
    size_t index = hash(key) & (capacity - 1);
    Entry entry = (Entry) {{ .key = key, .value = value, .offset = 0 }};
    size_t i = index;
    for( ; map->entries[i].key != EMPTY_{keyempty}_KEY; i = (i + 1) & (capacity - 1))
    {{
        if(entry.key == map->entries[i].key)
        {{
            map->entries[i].value = value;
            return;
        }}
        if(entry.offset > map->entries[i].offset)
        {{
            Entry temp = entry;
            entry = map->entries[i];
            map->entries[i] = temp;
        }}
        entry.offset++;
    }}
    map->entries[i] = entry;
    map->count++;
}}

{valt} {hmap}_get({hmap}* map, {keyt} key)
{{
    if(key == EMPTY_{keyempty}_KEY)
    {{
        if(map->emptyKeyPresent) return map->emptyKeyValue;
        else return -1;
    }}
    
    size_t capacity = map->capacity;
    size_t index = hash(key) & (capacity - 1);
    for(size_t i = index; map->entries[i].key != EMPTY_{keyempty}_KEY; i = (i + 1) & (capacity - 1))
    {{
        if(map->entries[i].key == key) return map->entries[i].value;
    }}
    return -1;
}}

void {hmap}_remove({hmap}* map, {keyt} key)
{{
    if(key == EMPTY_{keyempty}_KEY)
    {{
        map->emptyKeyPresent = false;
        return;
    }}
    
    size_t capacity = map->capacity;
    size_t index = hash(key) & (capacity - 1);
    bool deleted = false;
    size_t i = index, prevI;
    for( ; map->entries[i].key != EMPTY_{keyempty}_KEY && (!deleted || map->entries[i].offset != 0); 
        i = (i + 1) & (capacity - 1))
    {{
        if(map->entries[i].key == key)
        {{
            map->entries[i].key = EMPTY_{keyempty}_KEY;
            deleted = true;
        }}
        else if(deleted)
        {{
            map->entries[i].offset--;
            map->entries[prevI] = map->entries[i];
            map->entries[i].key = EMPTY_{keyempty}_KEY;
        }}
        prevI = i;
    }}
}}

void {hmap}_free({hmap}* map)
{{
    free(map->entries);
    free(map);
}}"""


headfile = open(hmap + '.h', 'w')
codefile = open(hmap + '.c', 'w')
headfile.write(header)
codefile.write(code)