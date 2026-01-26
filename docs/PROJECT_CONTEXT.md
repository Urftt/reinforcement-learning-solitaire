# Project Context

> **Purpose**: Help Claude Code understand the project's vision, goals, and current state across sessions.
> **Update frequency**: Update when project goals shift or major milestones are reached.

## Project Vision

**What problem does this solve?**

This is a learning project designed to build deep understanding of reinforcement learning algorithms through hands-on implementation. Rather than just reading about RL or using black-box libraries, this project emphasizes building algorithms from scratch to understand the fundamentals.

**What is the end goal?**

Successfully train RL agents to play increasingly complex games:
1. **Phase 1**: Master RL fundamentals with GridWorld (tabular Q-learning)
2. **Phase 2**: Build and train an agent for Klondike Solitaire using both tabular and deep RL methods

Success means: understanding RL concepts deeply, having clean reusable code, and achieving measurable performance (win rates, learning curves).

## Current Status

**Phase**: Planning / Initial Development

**Last Updated**: 2026-01-25

**Current Focus**:

Setting up Phase 1 - GridWorld environment and Q-learning implementation. Establishing project structure, visualization tools, and foundational code patterns that will scale to more complex projects.

**What Works**:
- [x] Project template structure set up
- [x] GridWorld environment implemented
- [ ] Q-learning agent implemented
- [ ] Visualization tools for learning progress
- [ ] Basic metrics tracking

**What Doesn't Work Yet**:
- [ ] Solitaire game environment
- [ ] Deep RL implementations (DQN, etc.)
- [ ] Advanced visualization dashboards

## Project Motivation

**Why this project?**

Learning by building. Reading papers and watching lectures is valuable, but implementing algorithms from scratch cements understanding. Solitaire is an interesting RL challenge with partial observability, large state spaces, and sparse rewards - perfect for pushing beyond basics.

**Personal Goals**:
- Deeply understand RL fundamentals: value functions, policy learning, exploration vs exploitation
- Build clean, reusable RL infrastructure (environments, agents, training loops)
- Master visualization of RL metrics (essential for debugging and understanding)
- Progress from tabular methods to deep RL (understand why/when to use each)
- Create a portfolio piece demonstrating RL expertise

## Constraints & Preferences

**Technical Preferences**:
- **Code style**: PEP8, clean and readable over clever
- **Implementation philosophy**: Build from scratch first, use libraries for comparison later
- **Visualization**: Essential - I'm a visual learner, need to see what's happening
- **Architecture**: Follow Gymnasium/OpenAI Gym interfaces for environments
- **Testing**: Important for correctness, especially for RL algorithms
- **Libraries**: NumPy, Matplotlib for basics; PyTorch for deep RL; Gymnasium for interfaces

**Time Constraints**:
Long-term learning project, no hard deadlines. Prefer to do things right over rushing.

**Scope Boundaries**:
- **In scope**: GridWorld, Klondike Solitaire, Q-learning, SARSA, DQN, visualization tools
- **Out of scope** (for now): Policy gradients, actor-critic, multi-agent RL, other card games
- Focus on understanding depth over algorithm breadth

## Notes for Claude Code

**How I want CC to help**:
- Maintain clean, well-structured code following best practices
- Explain RL concepts as we implement them (I want to learn deeply)
- Suggest visualizations that help understand what the agent is learning
- Help debug RL-specific issues (non-converging policies, reward hacking, etc.)
- Keep documentation updated as the project evolves
- Recommend good abstractions that will scale from GridWorld to Solitaire

**Things to watch out for**:
- Don't add features I didn't ask for - this is a learning project, I want to understand each piece
- Prioritize correctness over performance (I need to understand the algorithm first)
- Always implement visualizations alongside algorithms - seeing is understanding
- Watch for common RL pitfalls: reward scaling, exploration strategy, off-by-one errors in Bellman updates

**Communication preferences**:
- Explain the "why" behind implementation choices, especially RL-specific decisions
- Show me what we're building before diving into code
- Use code examples and diagrams when explaining concepts
- Ask questions if requirements are ambiguous rather than making assumptions
- I learn best by seeing things visually - suggest visualizations proactively
