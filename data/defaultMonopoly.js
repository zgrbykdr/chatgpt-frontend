export const defaultMonopoly = {
  meta: {
    name: 'Classic Monopoly',
    version: '1.0.0'
  },
  rules: {
    startingMoney: 1500,
    passGoAmount: 200,
    jailIndex: 10,
    goToJailIndex: 30,
    maxHouses: 4,
    houseRentMultiplier: 0.9,
    hotelRentMultiplier: 1.8
  },
  decks: [
    {
      id: 'chance',
      name: 'Chance',
      cards: [
        { id: 'ch1', description: 'Advance to GO. Collect $200.', actions: [{ type: 'moveTo', square: 0 }, { type: 'receiveMoney', amount: 200 }] },
        { id: 'ch2', description: 'Bank pays you dividend of $50.', actions: [{ type: 'receiveMoney', amount: 50 }] },
        { id: 'ch3', description: 'Go to Jail. Do not pass GO.', actions: [{ type: 'goToJail' }] },
        { id: 'ch4', description: 'Pay poor tax of $15.', actions: [{ type: 'payMoney', amount: 15 }] },
        { id: 'ch5', description: 'Take a trip to Illinois Avenue.', actions: [{ type: 'moveTo', square: 24 }] },
        { id: 'ch6', description: 'Advance token to nearest Railroad.', actions: [{ type: 'moveToNearest', category: 'railroad' }] }
      ]
    },
    {
      id: 'community',
      name: 'Community Chest',
      cards: [
        { id: 'cc1', description: 'Advance to GO. Collect $200.', actions: [{ type: 'moveTo', square: 0 }, { type: 'receiveMoney', amount: 200 }] },
        { id: 'cc2', description: 'Doctor\'s fees. Pay $50.', actions: [{ type: 'payMoney', amount: 50 }] },
        { id: 'cc3', description: 'From sale of stock you get $50.', actions: [{ type: 'receiveMoney', amount: 50 }] },
        { id: 'cc4', description: 'Go to Jail. Do not pass GO.', actions: [{ type: 'goToJail' }] },
        { id: 'cc5', description: 'It is your birthday. Collect $10 from every player.', actions: [{ type: 'receiveFromAllPlayers', amount: 10 }] },
        { id: 'cc6', description: 'Pay hospital fees of $100.', actions: [{ type: 'payMoney', amount: 100 }] }
      ]
    }
  ],
  board: {
    squares: [
      { id: 0, name: 'GO', type: 'go', actions: [{ type: 'receiveMoney', amount: 200 }] },
      { id: 1, name: 'Mediterranean Avenue', type: 'property', group: 'brown', price: 60, baseRent: 2, houseCost: 50 },
      { id: 2, name: 'Community Chest', type: 'draw', deckId: 'community' },
      { id: 3, name: 'Baltic Avenue', type: 'property', group: 'brown', price: 60, baseRent: 4, houseCost: 50 },
      { id: 4, name: 'Income Tax', type: 'tax', amount: 200 },
      { id: 5, name: 'Reading Railroad', type: 'property', category: 'railroad', group: 'railroad', price: 200, baseRent: 25 },
      { id: 6, name: 'Oriental Avenue', type: 'property', group: 'lightBlue', price: 100, baseRent: 6, houseCost: 50 },
      { id: 7, name: 'Chance', type: 'draw', deckId: 'chance' },
      { id: 8, name: 'Vermont Avenue', type: 'property', group: 'lightBlue', price: 100, baseRent: 6, houseCost: 50 },
      { id: 9, name: 'Connecticut Avenue', type: 'property', group: 'lightBlue', price: 120, baseRent: 8, houseCost: 50 },
      { id: 10, name: 'Jail / Just Visiting', type: 'jail' },
      { id: 11, name: 'St. Charles Place', type: 'property', group: 'pink', price: 140, baseRent: 10, houseCost: 100 },
      { id: 12, name: 'Electric Company', type: 'property', group: 'utility', price: 150, baseRent: 12 },
      { id: 13, name: 'States Avenue', type: 'property', group: 'pink', price: 140, baseRent: 10, houseCost: 100 },
      { id: 14, name: 'Virginia Avenue', type: 'property', group: 'pink', price: 160, baseRent: 12, houseCost: 100 },
      { id: 15, name: 'Pennsylvania Railroad', type: 'property', category: 'railroad', group: 'railroad', price: 200, baseRent: 25 },
      { id: 16, name: 'St. James Place', type: 'property', group: 'orange', price: 180, baseRent: 14, houseCost: 100 },
      { id: 17, name: 'Community Chest', type: 'draw', deckId: 'community' },
      { id: 18, name: 'Tennessee Avenue', type: 'property', group: 'orange', price: 180, baseRent: 14, houseCost: 100 },
      { id: 19, name: 'New York Avenue', type: 'property', group: 'orange', price: 200, baseRent: 16, houseCost: 100 },
      { id: 20, name: 'Free Parking', type: 'freeParking' },
      { id: 21, name: 'Kentucky Avenue', type: 'property', group: 'red', price: 220, baseRent: 18, houseCost: 150 },
      { id: 22, name: 'Chance', type: 'draw', deckId: 'chance' },
      { id: 23, name: 'Indiana Avenue', type: 'property', group: 'red', price: 220, baseRent: 18, houseCost: 150 },
      { id: 24, name: 'Illinois Avenue', type: 'property', group: 'red', price: 240, baseRent: 20, houseCost: 150 },
      { id: 25, name: 'B. & O. Railroad', type: 'property', category: 'railroad', group: 'railroad', price: 200, baseRent: 25 },
      { id: 26, name: 'Atlantic Avenue', type: 'property', group: 'yellow', price: 260, baseRent: 22, houseCost: 150 },
      { id: 27, name: 'Ventnor Avenue', type: 'property', group: 'yellow', price: 260, baseRent: 22, houseCost: 150 },
      { id: 28, name: 'Water Works', type: 'property', group: 'utility', price: 150, baseRent: 12 },
      { id: 29, name: 'Marvin Gardens', type: 'property', group: 'yellow', price: 280, baseRent: 24, houseCost: 150 },
      { id: 30, name: 'Go To Jail', type: 'goToJail', actions: [{ type: 'goToJail' }] },
      { id: 31, name: 'Pacific Avenue', type: 'property', group: 'green', price: 300, baseRent: 26, houseCost: 200 },
      { id: 32, name: 'North Carolina Avenue', type: 'property', group: 'green', price: 300, baseRent: 26, houseCost: 200 },
      { id: 33, name: 'Community Chest', type: 'draw', deckId: 'community' },
      { id: 34, name: 'Pennsylvania Avenue', type: 'property', group: 'green', price: 320, baseRent: 28, houseCost: 200 },
      { id: 35, name: 'Short Line', type: 'property', category: 'railroad', group: 'railroad', price: 200, baseRent: 25 },
      { id: 36, name: 'Chance', type: 'draw', deckId: 'chance' },
      { id: 37, name: 'Park Place', type: 'property', group: 'darkBlue', price: 350, baseRent: 35, houseCost: 200 },
      { id: 38, name: 'Luxury Tax', type: 'tax', amount: 100 },
      { id: 39, name: 'Boardwalk', type: 'property', group: 'darkBlue', price: 400, baseRent: 50, houseCost: 200 }
    ]
  }
};
