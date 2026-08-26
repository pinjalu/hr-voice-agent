# Aptitude Question Bank
# Structured by candidate type and difficulty

QUESTION_BANK = {
    "fresher": {
        "easy": [
            {
                "question": "What is the next number in the sequence: 2, 4, 8, 16, ...?",
                "options": {"A": "24", "B": "32", "C": "40", "D": "48"},
                "answer": "B",
                "explanation": "Multiplying by 2. 16 × 2 = 32.",
                "type": "sequence"
            },
            {
                "question": "If a shirt is discounted by 20% and now costs $80, what was its original price?",
                "options": {"A": "$90", "B": "$100", "C": "$110", "D": "$120"},
                "answer": "B",
                "explanation": "80 / 0.8 = 100",
                "type": "math"
            },
            {
                "question": "If all A are B and all B are C, are all A necessarily C?",
                "options": {"A": "Yes", "B": "No", "C": "Sometimes", "D": "Cannot determine"},
                "answer": "A",
                "explanation": "Logic syllogism - transitive property.",
                "type": "logic"
            },
            {
                "question": "Find the average: 10, 20, 30, 40, 50.",
                "options": {"A": "25", "B": "30", "C": "35", "D": "40"},
                "answer": "B",
                "explanation": "(10+20+30+40+50)/5 = 150/5 = 30",
                "type": "math"
            },
            {
                "question": "What is 15% of 200?",
                "options": {"A": "25", "B": "30", "C": "35", "D": "40"},
                "answer": "B",
                "explanation": "0.15 × 200 = 30",
                "type": "math"
            },
            {
                "question": "Complete the series: 1, 4, 9, 16, ...?",
                "options": {"A": "20", "B": "25", "C": "30", "D": "36"},
                "answer": "B",
                "explanation": "Square of 5 is 25. Pattern: 1², 2², 3², 4², 5²",
                "type": "sequence"
            },
            {
                "question": "If 5 workers can build a wall in 10 days, how many days will 10 workers take?",
                "options": {"A": "3 days", "B": "5 days", "C": "7 days", "D": "10 days"},
                "answer": "B",
                "explanation": "Inverse proportion: 5*10 / 10 = 5",
                "type": "work"
            },
            {
                "question": "Which word is an antonym of 'Brief'?",
                "options": {"A": "short", "B": "long", "C": "quick", "D": "fast"},
                "answer": "B",
                "explanation": "Brief means short, so antonym is long.",
                "type": "verbal"
            },
            {
                "question": "Solve: 25 * 4 - 10?",
                "options": {"A": "80", "B": "90", "C": "100", "D": "110"},
                "answer": "B",
                "explanation": "100 - 10 = 90",
                "type": "math"
            },
            {
                "question": "If tomorrow is Monday, what was the day before yesterday?",
                "options": {"A": "Wednesday", "B": "Thursday", "C": "Friday", "D": "Saturday"},
                "answer": "C",
                "explanation": "Tomorrow Monday -> Today Sunday -> Yesterday Sat -> Day before yesterday Friday",
                "type": "logic"
            },
            {
                "question": "What is the square root of 144?",
                "options": {"A": "10", "B": "12", "C": "14", "D": "16"},
                "answer": "B",
                "explanation": "12*12 = 144",
                "type": "math"
            },
            {
                "question": "If A=1, B=2, C=3, what is E+F?",
                "options": {"A": "9", "B": "10", "C": "11", "D": "12"},
                "answer": "C",
                "explanation": "E=5, F=6, so 5 + 6 = 11",
                "type": "logic"
            },
            {
                "question": "A train travels 60km in 1 hour. How many km in 15 minutes?",
                "options": {"A": "10 km", "B": "15 km", "C": "20 km", "D": "25 km"},
                "answer": "B",
                "explanation": "60 / 4 = 15",
                "type": "speed"
            },
            {
                "question": "Which of the following is a prime number?",
                "options": {"A": "9", "B": "15", "C": "17", "D": "21"},
                "answer": "C",
                "explanation": "17 has no divisors other than 1 and 17.",
                "type": "math"
            },
            {
                "question": "If you rearrange the letters 'CIFAIPC', you get the name of an:",
                "options": {"A": "mountain", "B": "ocean", "C": "river", "D": "desert"},
                "answer": "B",
                "explanation": "CIFAIPC rearranged is PACIFIC (an ocean)",
                "type": "logic"
            }
        ],
        "medium": [
            {
                "question": "A train 100m long passes a pole in 10 seconds. What is its speed in km/h?",
                "options": {"A": "30 km/h", "B": "36 km/h", "C": "40 km/h", "D": "45 km/h"},
                "answer": "B",
                "explanation": "10m/s * 3.6 = 36 km/h",
                "type": "speed"
            },
            {
                "question": "If the radius of a circle increases by 50%, by what percentage does the area increase?",
                "options": {"A": "100%", "B": "125%", "C": "150%", "D": "200%"},
                "answer": "B",
                "explanation": "1.5^2 = 2.25, increase is 1.25 or 125%",
                "type": "math"
            },
            {
                "question": "A man buys a cycle for $1000 and sells it for $1200. What is his profit percentage?",
                "options": {"A": "15%", "B": "20%", "C": "25%", "D": "30%"},
                "answer": "B",
                "explanation": "200/1000 * 100 = 20%",
                "type": "profit"
            },
            {
                "question": "Find the missing number: 3, 7, 15, 31, ...?",
                "options": {"A": "55", "B": "63", "C": "71", "D": "79"},
                "answer": "B",
                "explanation": "2n + 1 pattern: 2*31 + 1 = 63",
                "type": "sequence"
            },
            {
                "question": "If 3 men or 6 women can do a work in 20 days, how long will 1 man and 8 women take?",
                "options": {"A": "10 days", "B": "12 days", "C": "15 days", "D": "18 days"},
                "answer": "B",
                "explanation": "Calculated worker days.",
                "type": "work"
            },
            {
                "question": "The ratio of two numbers is 3:4. If their sum is 70, find the numbers.",
                "options": {"A": "20, 50", "B": "25, 45", "C": "30, 40", "D": "35, 35"},
                "answer": "C",
                "explanation": "3x+4x=70 -> 7x=70 -> x=10, so numbers are 30 and 40",
                "type": "ratio"
            },
            {
                "question": "A clock shows 3:00. What is the angle between the hands?",
                "options": {"A": "75 degrees", "B": "90 degrees", "C": "105 degrees", "D": "120 degrees"},
                "answer": "B",
                "explanation": "3 * 30 degrees = 90",
                "type": "logic"
            },
            {
                "question": "If 1st January 2023 was Sunday, what day was 1st February 2023?",
                "options": {"A": "Monday", "B": "Tuesday", "C": "Wednesday", "D": "Thursday"},
                "answer": "C",
                "explanation": "31 days = 4 weeks + 3 days. Sun+3 = Wed.",
                "type": "logic"
            },
            {
                "question": "Find the odd one out: 27, 64, 125, 144.",
                "options": {"A": "27", "B": "64", "C": "125", "D": "144"},
                "answer": "D",
                "explanation": "The others are cubes (3^3, 4^3, 5^3). 144 is 12^2.",
                "type": "logic"
            },
            {
                "question": "If PRINTER is coded as RPINETR, how is MONITOR coded?",
                "options": {"A": "OMINOTR", "B": "NOMIOTR", "C": "MONIOTR", "D": "OMNIOTR"},
                "answer": "A",
                "explanation": "Swapping adjacent pairs.",
                "type": "logic"
            },
            {
                "question": "Simple interest on $5000 at 10% for 2 years is?",
                "options": {"A": "$800", "B": "$1000", "C": "$1200", "D": "$1500"},
                "answer": "B",
                "explanation": "5000 * 0.1 * 2 = 1000",
                "type": "math"
            },
            {
                "question": "A boat goes 10 km upstream in 2 hours. Speed of boat in still water is 8km/h. Speed of stream?",
                "options": {"A": "2 km/h", "B": "3 km/h", "C": "4 km/h", "D": "5 km/h"},
                "answer": "B",
                "explanation": "8-x = 5 -> x=3",
                "type": "speed"
            },
            {
                "question": "Probability of getting a sum of 7 when rolling two dice?",
                "options": {"A": "1/12", "B": "1/6", "C": "1/4", "D": "1/3"},
                "answer": "B",
                "explanation": "6/36 = 1/6",
                "type": "prob"
            },
            {
                "question": "What is the HCF of 12 and 18?",
                "options": {"A": "4", "B": "6", "C": "9", "D": "12"},
                "answer": "B",
                "explanation": "Common factor is 6.",
                "type": "math"
            },
            {
                "question": "Number of squares in a 3x3 grid?",
                "options": {"A": "12", "B": "14", "C": "16", "D": "18"},
                "answer": "B",
                "explanation": "9 (1x1) + 4 (2x2) + 1 (3x3) = 14",
                "type": "logic"
            }
        ],
        "hard": [
            {
                "question": "A bag contains 5 red and 3 blue balls. If two balls are drawn, what is the probability both are red?",
                "options": {"A": "3/14", "B": "5/14", "C": "7/14", "D": "9/14"},
                "answer": "B",
                "explanation": "(5/8) * (4/7) = 20/56 = 5/14",
                "type": "prob"
            },
            {
                "question": "A sum of money doubles itself in 5 years at compound interest. In how many years will it become 8 times?",
                "options": {"A": "10 years", "B": "15 years", "C": "20 years", "D": "25 years"},
                "answer": "B",
                "explanation": "2^3 = 8, so 5 * 3 = 15 years.",
                "type": "math"
            },
            {
                "question": "The speed of a train is 50% more than a car. Both start at A and reach B 75km away at the same time. The train stops for 12.5 mins. Speed of car?",
                "options": {"A": "100 km/h", "B": "120 km/h", "C": "140 km/h", "D": "160 km/h"},
                "answer": "B",
                "explanation": "Time difference calculation.",
                "type": "speed"
            },
            {
                "question": "How many ways can the letters of 'APPLE' be rearranged?",
                "options": {"A": "48", "B": "60", "C": "72", "D": "120"},
                "answer": "B",
                "explanation": "5! / 2! = 120 / 2 = 60",
                "type": "math"
            },
            {
                "question": "Find the unit digit of 3 raised to the power 40?",
                "options": {"A": "1", "B": "3", "C": "7", "D": "9"},
                "answer": "A",
                "explanation": "Cycle: 3, 9, 7, 1. 40 is multiple of 4.",
                "type": "math"
            },
            {
                "question": "Find the number of zeros at the end of 100 factorial.",
                "options": {"A": "20", "B": "24", "C": "28", "D": "32"},
                "answer": "B",
                "explanation": "100/5 + 100/25 = 20 + 4 = 24",
                "type": "math"
            },
            {
                "question": "A mixture contains milk and water in ratio 5:1. If 5L water is added, ratio becomes 5:2. Original milk quantity?",
                "options": {"A": "20L", "B": "25L", "C": "30L", "D": "35L"},
                "answer": "B",
                "explanation": "5x/(x+5) = 5/2 -> 10x=5x+25 -> x=5. Milk = 25.",
                "type": "math"
            },
            {
                "question": "In a group of 15, 7 can speak Spanish, 8 can speak French and 3 can speak neither. How many speak both?",
                "options": {"A": "1", "B": "2", "C": "3", "D": "4"},
                "answer": "C",
                "explanation": "15-3 = 12 speakers. 7+8-x=12 -> x=3.",
                "type": "logic"
            },
            {
                "question": "What is the angle between the hands of a clock at 5:40?",
                "options": {"A": "60 degrees", "B": "70 degrees", "C": "80 degrees", "D": "90 degrees"},
                "answer": "B",
                "explanation": "|(30*5) - (5.5*40)| = |150 - 220| = 70",
                "type": "math"
            },
            {
                "question": "The average age of 10 students is 15. If a teacher's age is added, average becomes 16. Teacher's age?",
                "options": {"A": "24", "B": "26", "C": "28", "D": "30"},
                "answer": "B",
                "explanation": "11*16 - 10*15 = 176 - 150 = 26",
                "type": "math"
            }
        ]
    },
    "experienced": {
        "easy": [
            {
                "question": "If a system handles 100 requests per second and each request takes 200ms of processing, how many threads are working concurrently on average?",
                "options": {"A": "15", "B": "20", "C": "25", "D": "30"},
                "answer": "B",
                "explanation": "Little's Law: 100 * 0.2 = 20",
                "type": "logic"
            },
            {
                "question": "In a min-heap data structure, where is the second smallest element always located?",
                "options": {"A": "root", "B": "level 1", "C": "level 2", "D": "any leaf"},
                "answer": "B",
                "explanation": "The children of the root (index 1 or 2).",
                "type": "ds"
            },
            {
                "question": "If 5 servers can process 5000 requests in 5 minutes, how many minutes will it take 100 servers to process 100,000 requests?",
                "options": {"A": "3 minutes", "B": "5 minutes", "C": "7 minutes", "D": "10 minutes"},
                "answer": "B",
                "explanation": "Scale is linear. Each server does 1000 per 5 mins. 100 * 1000 = 100k.",
                "type": "logic"
            },
            {
                "question": "A database index speeds up reads but slows down what internal operation?",
                "options": {"A": "reads", "B": "writes", "C": "deletes", "D": "queries"},
                "answer": "B",
                "explanation": "Index needs to be updated on Every INSERT/UPDATE.",
                "type": "db"
            },
            {
                "question": "What is the time complexity of looking up a key in a well-distributed Hash Map?",
                "options": {"A": "O(log n)", "B": "O(1)", "C": "O(n)", "D": "O(n log n)"},
                "answer": "B",
                "explanation": "Constant time lookup.",
                "type": "ds"
            },
            {
                "question": "If A depends on B, and B depends on C, and C depends on A, what is this situation called in architecture?",
                "options": {"A": "dependency chain", "B": "circular dependency", "C": "layered architecture", "D": "modular design"},
                "answer": "B",
                "explanation": "Dependency loop.",
                "type": "arch"
            },
            {
                "question": "Which sorting algorithm has a guaranteed O(n log n) time complexity even in the worst case?",
                "options": {"A": "Quick Sort", "B": "Merge Sort", "C": "Bubble Sort", "D": "Insertion Sort"},
                "answer": "B",
                "explanation": "Merge Sort has consistent O(n log n) performance in all cases.",
                "type": "algo"
            },
            {
                "question": "If you have 1000 records and a Binary Search is performed, what is the maximum number of comparisons needed?",
                "options": {"A": "8", "B": "10", "C": "12", "D": "15"},
                "answer": "B",
                "explanation": "log2(1000) is approx 10.",
                "type": "algo"
            },
            {
                "question": "What is the result of '1' + 1 in JavaScript?",
                "options": {"A": "2", "B": "11", "C": "'11'", "D": "Error"},
                "answer": "B",
                "explanation": "String concatenation: '1' + 1 = '11'",
                "type": "code"
            },
            {
                "question": "If a server's availability is 90%, and you add an identical redundant server, what is the new total availability percentage?",
                "options": {"A": "95%", "B": "99%", "C": "99.9%", "D": "100%"},
                "answer": "B",
                "explanation": "1 - (0.1 * 0.1) = 0.99 = 99%",
                "type": "logic"
            }
        ],
        "medium": [
            {
                "question": "You have a sorted array of 1 million integers. You need to find if a specific number exists. How many steps will it take at most?",
                "options": {"A": "15", "B": "20", "C": "25", "D": "30"},
                "answer": "B",
                "explanation": "log2(1,000,000) is approx 20.",
                "type": "algo"
            },
            {
                "question": "A cache has a hit rate of 80%. Cache access takes 1ms, and DB access takes 100ms. What is the average latency?",
                "options": {"A": "18ms", "B": "21ms", "C": "25ms", "D": "30ms"},
                "answer": "B",
                "explanation": "(0.8 * 1) + (0.2 * 101) = 0.8 + 20.2 = 21ms.",
                "type": "logic"
            },
            {
                "question": "If a function is called recursively without a base case, what error will eventually occur?",
                "options": {"A": "null pointer exception", "B": "stack overflow", "C": "out of memory", "D": "infinite loop"},
                "answer": "B",
                "explanation": "Memory limit of stack reached.",
                "type": "code"
            },
            {
                "question": "In a distributed system, if you increase Consistency, which other property of the CAP theorem usually decreases?",
                "options": {"A": "Partition tolerance", "B": "availability", "C": "scalability", "D": "reliability"},
                "answer": "B",
                "explanation": "Trade-off in partitioned networks.",
                "type": "arch"
            },
            {
                "question": "How many bits are used in an IPv4 address?",
                "options": {"A": "16", "B": "32", "C": "64", "D": "128"},
                "answer": "B",
                "explanation": "4 octets of 8 bits each = 32 bits.",
                "type": "network"
            },
            {
                "question": "If you need to store 10 million 'True/False' flags with minimum memory, which data structure is best?",
                "options": {"A": "array", "B": "bitset", "C": "hash set", "D": "linked list"},
                "answer": "B",
                "explanation": "Uses 1 bit per flag.",
                "type": "ds"
            },
            {
                "question": "What happens to the time complexity of a Hash Map if every key results in the same hash code?",
                "options": {"A": "O(1)", "B": "O(log n)", "C": "O(n)", "D": "O(n log n)"},
                "answer": "C",
                "explanation": "Becomes a linked list.",
                "type": "ds"
            },
            {
                "question": "A system uses a Load Balancer. If one server out of 4 fails, what percentage of traffic must the remaining servers absorb?",
                "options": {"A": "25%", "B": "33%", "C": "40%", "D": "50%"},
                "answer": "B",
                "explanation": "Each takes 1/3 more of their current load.",
                "type": "logic"
            },
            {
                "question": "If 10 machines take 10 minutes to make 10 widgets, how long does it take 100 machines to make 100 widgets?",
                "options": {"A": "5 minutes", "B": "10 minutes", "C": "15 minutes", "D": "20 minutes"},
                "answer": "B",
                "explanation": "Rate remains the same per machine.",
                "type": "logic"
            },
            {
                "question": "What is the difference between a Process and a Thread regarding memory?",
                "options": {"A": "Both share memory", "B": "Threads share memory, Processes have private memory", "C": "Both have private memory", "D": "No difference"},
                "answer": "B",
                "explanation": "Isolation vs Sharing.",
                "type": "os"
            }
        ],
        "hard": [
            {
                "question": "You need to find the top 10 most frequent words in a 100GB file using only 1GB of RAM. What is the high-level approach?",
                "options": {"A": "load entire file", "B": "external sort or streaming hash", "C": "use database", "D": "split into 100 files"},
                "answer": "B",
                "explanation": "Divide and conquer or frequency counting.",
                "type": "arch"
            },
            {
                "question": "Design a system to generate unique IDs at a rate of 100k per second across multiple data centers. What is a common algorithm for this?",
                "options": {"A": "UUID", "B": "snowflake", "C": "auto-increment", "D": "random generator"},
                "answer": "B",
                "explanation": "Standard distributed ID generation.",
                "type": "arch"
            },
            {
                "question": "If an algorithm's complexity is T(n) = 2T(n/2) + n, what is its Big-O notation?",
                "options": {"A": "O(n)", "B": "O(n log n)", "C": "O(n²)", "D": "O(log n)"},
                "answer": "B",
                "explanation": "Master Theorem case 2.",
                "type": "algo"
            },
            {
                "question": "In a microservices architecture, how do you handle a transaction spanning across three different services?",
                "options": {"A": "two-phase commit", "B": "saga pattern", "C": "single transaction", "D": "no transaction"},
                "answer": "B",
                "explanation": "Distributed transaction management.",
                "type": "arch"
            },
            {
                "question": "What is the main problem solved by the 'Raft' or 'Paxos' algorithms?",
                "options": {"A": "load balancing", "B": "consensus", "C": "caching", "D": "routing"},
                "answer": "B",
                "explanation": "Distributed agreement.",
                "type": "arch"
            },
            {
                "question": "If you have 10 billion URLs and need to check if a new URL has been seen before with 99% accuracy using minimal memory, what structure do you use?",
                "options": {"A": "hash set", "B": "bloom filter", "C": "trie", "D": "array"},
                "answer": "B",
                "explanation": "Probabilistic set membership.",
                "type": "ds"
            }
        ]
    }
}
