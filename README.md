# Market Asset Trading Experiment System

## Overview

This is an experimental economics application built on the oTree 5 framework, designed to study asset market trading behavior under uncertainty. The system implements a Continuous Double Auction market supporting multi-round, multi-asset trading experiments under both Risk and Ambiguity conditions.

## Key Features

### 1. Experimental Design Framework
- **Multi-Round Trading**: Support for up to 10 experimental rounds with independent parameter configurations
- **Multi-Asset Support**: Simultaneous trading of up to 4 different assets (A, B, C, D)
- **Flexible Configuration**: CSV-based parameter settings without code modification
- **SSW Market Support**: Optional inheritance of assets and cash from previous rounds

### 2. Uncertainty Condition Design

#### Risk Condition
- Explicit probability distributions: States and probabilities are fully displayed
- Transparent dividend payment probabilities
- Page 1: 25% probability of no dividend (black), 75% probability of dividend (white)
- Page 2: Three dividend levels each with 33.33% probability (red, yellow, blue)

#### Ambiguity Condition
- Unclear probability distributions: Partial information is obscured
- Participants cannot fully know true probabilities
- Implemented by hiding rows in the probability matrix

### 3. Dividend Determination Mechanism

**Two-Stage Drawing Process**:

1. **Stage 1 (DividendPage1)**:
   - Each participant clicks on one cell in a 12×12 matrix
   - System randomly selects one participant's result
   - If black: Assets pay no dividend, proceed directly to market trading
   - If white: Proceed to Stage 2

2. **Stage 2 (DividendPage2)**:
   - Only executed if white was drawn in Stage 1
   - Participants click on another 12×12 matrix
   - System randomly selects one participant's result
   - Red/Yellow/Blue correspond to different dividend levels

### 4. Market Trading System

#### Continuous Double Auction Mechanism
- **Real-time Matching**: Buy and sell orders automatically matched
- **Price Priority**: Better prices execute first
- **Time Priority**: Earlier orders execute first at same price
- **Instant Trading**: Participants can submit limit orders (Maker) or market orders (Taker)

#### Order Types
- **Bid**: Offer to buy assets
- **Ask**: Offer to sell assets
- **Limit Order (Maker)**: Order waits in book for execution
- **Market Order (Taker)**: Immediate execution

#### Trading Constraints
- **Cash Constraint**: Total bid amount cannot exceed available cash
- **Asset Constraint**: Number of asks cannot exceed held assets
- **Self-Trading Check**: Prevents bidding higher than own asks or asking lower than own bids

### 5. Data Collection

The system automatically records:
- Detailed information on all orders (bids/asks)
- All transaction records (price, quantity, timestamp)
- Each participant's trading history
- Dividend drawing results for each round
- Initial and final asset holdings for each participant

### 6. User Interface

- **Real-time Market Information**: Current best bid/ask, order book depth
- **Personal Trading Interface**: Submit orders, cancel orders
- **Trading History**: View personal and market transaction records
- **Asset Status**: Real-time display of cash and asset holdings
- **Dividend Information**: Display asset returns under each state

## Technical Architecture

### Core Technology Stack
- **Framework**: oTree 5.x (Django-based experimental economics framework)
- **Backend**: Python 3.x
- **Frontend**: HTML5, JavaScript, Bootstrap
- **Database**: oTree built-in database (default SQLite, configurable PostgreSQL)
- **Real-time Communication**: WebSocket (via oTree channels)

### Key Modules

#### 1. Configuration Manager (configmanager.py)
- CSV configuration file parsing
- Parameter validation and type conversion
- Caching mechanism for performance

#### 2. Market Logic (mk.py)
- Order management: Create, cancel, validate
- Trade matching: Price matching, time priority
- State updates: Order book, transaction records

#### 3. Main Program (__init__.py)
- oTree model definitions: Subsession, Group, Player
- Page flow control
- Dividend drawing logic
- Data persistence

## File Structure

```
market1123/
├── __init__.py              # Main program: Model definitions and page logic
├── mk.py                    # Market trading logic module
├── configmanager.py         # Configuration file manager
├── configs/
│   └── demo.csv            # Experiment configuration file (round parameters)
├── Market.html             # Market trading page
├── DividendPage1.html      # Dividend drawing page 1
├── DividendPage2.html      # Dividend drawing page 2
├── Instruction.html        # Instruction page
├── RoundResults.html       # Round results page
├── FinalResults.html       # Final results page
├── Questionnaire.html      # Questionnaire page
└── Demographic.html        # Demographics page
```

## Configuration Guide

### CSV Configuration File Format

`configs/demo.csv` contains the following fields:

| Field | Type | Description |
|-------|------|-------------|
| round_number | int | Round number |
| period_length | int | Trading duration (seconds) |
| num_assets | int | Number of asset types (1-4) |
| num_states | int | Number of states |
| asseta_endowments | str | Initial Asset A allocation (9 space-separated numbers) |
| assetb_endowments | str | Initial Asset B allocation |
| cash_endowment | str | Initial cash allocation (9 space-separated numbers) |
| practice | bool | Whether this is a practice round |
| a1, a2, a3 | int | Asset A dividends in states 1-3 |
| b1, b2, b3 | int | Asset B dividends in states 1-3 |
| p0, p1, p2, p3 | float | State probabilities |
| state_independent | bool | Whether asset states are independent |
| ssw_inherit | bool | Whether to inherit holdings from previous round |
| treatment | str | Experimental treatment (e.g., "risk_risk", "risk_ambi") |

### Treatment Coding

Treatment field format: `{part1}_{part2}`

- **part1**: Uncertainty type for Stage 1 (whether dividend is paid)
- **part2**: Uncertainty type for Stage 2 (dividend level)

Options:
- `risk`: Risk (known probabilities)
- `ambi`: Ambiguity (unknown probabilities)

Examples:
- `risk_risk`: Both stages are risk
- `risk_ambi`: Stage 1 is risk, Stage 2 is ambiguity
- `ambi_risk`: Stage 1 is ambiguity, Stage 2 is risk
- `ambi_ambi`: Both stages are ambiguity

## Usage Instructions

### 1. Environment Setup

```bash
# Install oTree (requires Python 3.8+)
pip install otree

# Navigate to project directory
cd market1123
```

### 2. Configure Experiment

Edit `configs/demo.csv` file to set:
- Number of rounds and duration
- Initial asset and cash allocations
- Dividend levels
- Experimental conditions (risk/ambi)

### 3. Run Experiment

```bash
# Development mode
otree devserver

# Production mode
otree prodserver
```

### 4. Access Experiment

Open in browser:
- Development mode: `http://localhost:8000`
- Follow prompts to create session and distribute participant links

### 5. Export Data

```bash
# Export all data
otree export

# Or export via Web interface (Data page)
```

## Experimental Flow

1. **Welcome Page**: Introduction to the experiment
2. **Instruction Page**: Detailed rules and operation guide
3. **Wait Page**: Wait for all participants to be ready
4. **Dividend Page 1**: Determine whether dividend is paid
5. **Dividend Page 2**: Determine dividend level (if applicable)
6. **Market Trading**: Fixed-duration trading phase
7. **Round Results**: Display trading and earnings for this round
8. Repeat steps 3-7 (multiple rounds)
9. **Questionnaire**: Collect strategies and feedback
10. **Demographics**: Collect basic information
11. **Final Results**: Display total earnings and payment information

## Data Structure

### Key Data Models

#### Subsession
- Round configuration parameters
- Dividend drawing results
- State information

#### Group
- Order book state (trader_state)
- Trading history (trader_state_history)
- Dividend drawing results

#### Player
- Asset holdings (settled_assets)
- Cash holdings (settled_cash)
- Click selection records
- Questionnaire responses

## Distinctive Features

### 1. Dynamic Probability Display
- Precise probabilities shown under risk conditions
- Partial information hidden under ambiguity conditions
- Visual matrix interface

### 2. Real-time Trading Feedback
- Instant response to order submissions
- Real-time trade notifications
- Dynamic market state updates

### 3. Flexible Experimental Design
- Support for multiple treatment combinations
- Configurable parameter system
- Adaptable to different research needs

### 4. Complete Data Tracking
- Timestamp for every order
- Complete transaction chain
- Facilitates subsequent analysis

## Research Applications

This system can be used to study:
- Ambiguity Aversion
- Asset pricing behavior
- Market microstructure
- Effects of information asymmetry
- Risk preference measurement

## Technical Highlights

1. **High Performance**: Optimized with caching and async processing
2. **Extensible**: Modular design facilitates adding new features
3. **Stability**: Comprehensive error handling and data validation
4. **User-Friendly**: Intuitive interface and clear feedback
5. **Data Integrity**: Comprehensive recording of experimental process

## Important Notes

1. **Participant Count**: Currently set to 9 players per group; modifiable via `PLAYERS_PER_GROUP` in code
2. **Time Settings**: Ensure trading duration is sufficient for participants to complete trades
3. **Network Requirements**: Stable network connection required for real-time communication
4. **Browser Compatibility**: Latest versions of Chrome or Firefox recommended
5. **Data Backup**: Regularly export and backup experimental data

## License

This project is for academic research purposes.

## Contact

For questions or suggestions, please contact via GitHub Issues.
