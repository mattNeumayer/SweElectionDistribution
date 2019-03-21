import numpy as np
import matplotlib.pyplot as plt


def calc_saint_lague_method(votes, party_names, party_colors, num_seats, first_divisor=1.2):
    max_extra_seats = 6

    num_parties = votes.shape[0]
    assert(num_parties == party_names.shape[0])
    assert(num_parties == party_colors.shape[0])
    assert(num_seats > 0)

    divisors = 1.0 + np.array(range(num_seats + max_extra_seats)) * 2
    divisors[0] = first_divisor

    # Calculate all possible quotients and sort them (sorting flattens the matrix).
    quotients = votes[:, None] / divisors
    quotients_descending = np.argsort(quotients, axis=None)[::-1]

    # Convert flattened indices back to the 2D shape.
    # The first array is the party dim, the second the divisor dim.
    max_quotients_2d = np.unravel_index(quotients_descending, quotients.shape)
    party_dim = max_quotients_2d[0]
    divisor_dim = max_quotients_2d[1]

    # Iterate over the largest quotients and assign a seat to the corresponding party.
    seats_per_party = np.zeros(num_parties, np.uint32)
    for i in range(num_seats):
        seats_per_party[party_dim[i]] += 1

    # Print results
    print()
    print("Party\tSeats\t(%Seat\t%Vote\tLast Quot)")
    for p in range(num_parties):
        print("%5s\t%5d \t(%2.2f\t%2.2f\t%.2f)" % (
            party_names[p],
            seats_per_party[p],
            seats_per_party[p] / float(num_seats) * 100,
            votes[p] / votes.sum() * 100,
            quotients[p, seats_per_party[p]-1]
        ))

    # Calculate votes needed to gain seats.
    # This is equivalent to beating the quotient of the last awarded seat.
    votes_needed = np.zeros([num_parties, max_extra_seats - 1])
    for p in range(num_parties):
        for extra_seats_wanted in range(1, max_extra_seats):

            # This is a bit tricky:
            # We try to gain seats by overtaking the last n seats.
            # BUT, if the seat we overtake is already our own, we don't actually gain a seat.
            # Think about it this way:
            # 1. We remove ourselves from the quotient calculation, while keeping the other parties static.
            # 2. We find the n-last quotient value and have to beat that to gain n extra seats.
            seats_to_overtake = 0
            extra_seats_gotten = 0
            while extra_seats_gotten < extra_seats_wanted:
                seats_to_overtake += 1
                # The last quotient that got a seat is at index 'num_seats - 1' and we go backwards from there.
                if p != party_dim[num_seats - seats_to_overtake]:
                    extra_seats_gotten += 1

            quotient_to_overtake = quotients[party_dim[num_seats - seats_to_overtake],
                                             divisor_dim[num_seats - seats_to_overtake]]

            total_seats_wanted = seats_per_party[p] + seats_to_overtake

            # We calculate the votes needed to gap the difference of the quotients.
            # Note: Of course, as we gain more seats the final divisor also increases.
            quotient_diff = quotient_to_overtake - quotients[p, total_seats_wanted - 1]
            votes_needed[p, extra_seats_wanted - 1] = np.ceil((quotient_diff * divisors[total_seats_wanted - 1]))

    # Print output
    print()
    for extra_seats_wanted in range(1, max_extra_seats):
        print("Extra seats: %d" % extra_seats_wanted)
        for p in range(num_parties):
            print("\t%4s: %10d votes needed" % (party_names[p], votes_needed[p, extra_seats_wanted - 1]))

    # Plot output
    plt.figure(figsize=(10, 8))
    plt.subplot(211)
    for p in range(num_parties):
        plt.bar(np.array(range(1, max_extra_seats)) + 0.1 * p - 0.35,
                votes_needed[p, :],
                width=0.09,
                color=party_colors[p])

    plt.legend(party_names)
    plt.xticks(range(1, max_extra_seats))
    plt.title("Votes required to gain seats")
    plt.ylabel("Additional votes required")
    plt.xlabel("Seats gained")

    # Calculate votes needed to loose seats.
    # This is equivalent to losing against the quotient behind the last awarded seat.
    votes_needed = np.zeros([num_parties, max_extra_seats - 1])
    for p in range(num_parties):
        for seats_lost_wanted in range(1, max_extra_seats):

            # Same as above but starting with the seat after the last awarded one and going in opposite direction.
            seats_to_fall_behind = 0
            seats_lost_gotten = 0
            while seats_lost_gotten < seats_lost_wanted:
                seats_to_fall_behind += 1
                if p != party_dim[num_seats - 1 + seats_to_fall_behind]:
                    seats_lost_gotten += 1

            quotient_to_lose = quotients[party_dim[num_seats - 1 + seats_to_fall_behind],
                                         divisor_dim[num_seats - 1 + seats_to_fall_behind]]

            total_wanted_seats = seats_per_party[p] - seats_to_fall_behind

            # We calculate the votes required to be lost to gap the difference of the quotients.
            # Note: As we loose seats the final divisor decreases
            # and the quotient that should lose is the one after the last seat we get (!)
            # i.e. 'total_wanted_seats - 1 + 1'.
            quotient_diff = quotients[p, total_wanted_seats] - quotient_to_lose
            votes_needed[p, seats_lost_wanted - 1] = np.ceil(quotient_diff * divisors[total_wanted_seats])

    # Print output
    print()
    for extra_seats_wanted in range(1, max_extra_seats):
        print("Lost seats: %d" % extra_seats_wanted)
        for p in range(num_parties):
            print("\t%4s: %10d lost votes needed" % (party_names[p], votes_needed[p, extra_seats_wanted - 1]))

    # Plot output
    plt.subplot(212)
    for p in range(num_parties):
        plt.bar(np.array(range(1, max_extra_seats)) + 0.1 * p - 0.35,
                -votes_needed[p, :],
                width=0.09,
                color=party_colors[p])

    plt.legend(party_names)
    plt.xticks(range(1, max_extra_seats))
    plt.title("Votes required to lose seats")
    plt.ylabel("Additional votes required")
    plt.xlabel("Seats lost")
    plt.savefig("output.png")
    plt.show()


def calc_2018_election():
    votes = np.array([1284698, 557500, 355546, 409478, 1830386, 518454, 285899, 1135627])
    party_names = np.array(['M', 'C', 'L', 'KD', 'S', 'V', 'MP', 'SD'])
    party_colors = np.array(['#66BEE6', '#63A91D', '#3399FF', '#1B5CB1', '#FF0000', '#C40000', '#008000', '#DDDD00'])
    calc_saint_lague_method(votes, party_names, party_colors, 349)


if __name__ == '__main__':
    calc_2018_election()
