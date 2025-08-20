<!-- PROJECT LOGO -->
<h3 align="center">Clash Royale Bot</h3>

  <p align="center">
    Bot that plays Clash Royale and learns by playing games
    <br />
    <a href="https://github.com/krazyness/CRBot-public"><strong>Explore the docs »</strong></a>
    <br />
    <a href="https://github.com/krazyness/CRBot-public/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    &middot;
    <a href="https://github.com/krazyness/CRBot-public/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

A Python-based Clash Royale AI bot that learns and improves through gameplay. This project aims to help others understand machine learning, reinforcement learning, and game automation in a practical context.

*(Disclaimer: This project is not affiliated with Supercell. Use at your own risk—automated gameplay may violate Clash Royale's Terms of Service.)*

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With

* [![PyTorch][PyTorch.org]][PyTorch-url]
* [![Docker][Docker.com]][Docker-url]
* [![Roboflow][Roboflow.com]][Roboflow-url]
* [![Python][Python.org]][Python-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

### Prerequisites

* Windows (since that's the only OS it works on right now)
* VSCode (unless you're more familiar with other code editors)
* [Docker](https://www.docker.com/)
* [Roboflow Account](https://www.roboflow.com/)
* [BlueStacks](https://www.bluestacks.com/download.html) with ADB enabled
* [Python 3.12](https://www.python.org/downloads/windows/)
* Install the requirements:
```
pip install -r requirements.txt
``` 
  
### Installation

1. Create a Roboflow account as well as a workspace, then get your API key
![roboflow-tutorial](https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExNG1uNmtiaTAzamVvNnQwc2k3NDQzOXhzcmhxc2prZTBzM3U3YWY5YyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/1KLeC2gw8pimdhH61C/giphy.gif)
2. Clone the repo
   ```sh
   git clone https://github.com/krazyness/CRBot-public.git
   ```
3. Set up your environment variables:
   - Copy `.env.example` to `.env`
   - Edit `.env` and replace `your_roboflow_api_key_here` with your actual Roboflow private API key
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env and add your API key
   ROBOFLOW_API_KEY=your_actual_api_key_here
   ```
4. Fork both workflows:
[Troop Detection](https://app.roboflow.com/workflows/embed/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ3b3JrZmxvd0lkIjoiTEx3TjlnOEduenBjWmVYSktKYzEiLCJ3b3Jrc3BhY2VJZCI6Ik5vVUlkM3gyYWRSU0tqaURrM0ZMTzlBSmE1bzEiLCJ1c2VySWQiOiJOb1VJZDN4MmFkUlNLamlEazNGTE85QUphNW8xIiwiaWF0IjoxNzUzODgxNTcyfQ.-ZO7pqc3mBX6W49-uThUSBLdUaCRzM9I8exfEu6-lo8)
[Card Detection](https://app.roboflow.com/workflows/embed/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ3b3JrZmxvd0lkIjoiMEFmeVpSQ3FSS1dhV1J5QTFGNkciLCJ3b3Jrc3BhY2VJZCI6InJtZHNiY2xlU292aEEwNm15UDFWIiwidXNlcklkIjoiTm9VSWQzeDJhZFJTS2ppRGszRkxPOUFKYTVvMSIsImlhdCI6MTc1Mzg4MjE4Mn0.ceYp4JZoNSIrDkrX2vuc9or3qVakNexseYEgacIrfLA)

![Workspace-Fork-Tutorial](https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExM2g4NTZ2MDlkM3JpdGl5emgxNHc3ejJudTRiMDFnbXFkNmxnNzgyeSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/94yt100mNmhRIPRu3d/giphy.gif)

5. Get the workspace names from your forked workflows and update your `.env` file:
   - For the Troop Detection workspace, update `WORKSPACE_TROOP_DETECTION=your-troop-workspace-name`
   - For the Card Detection workspace, update `WORKSPACE_CARD_DETECTION=your-card-workspace-name`
   
   Your `.env` file should look like:
   ```bash
   ROBOFLOW_API_KEY=your_actual_api_key_here
   WORKSPACE_TROOP_DETECTION=workspace-your-troop-name
   WORKSPACE_CARD_DETECTION=workspace-your-card-name
   ```

6. **Set up ADB connection with BlueStacks:**
   ```bash
   python setup_adb.py
   ```
   This script will:
   - Find your ADB installation automatically
   - Start the ADB server
   - Connect to BlueStacks
   - Test the connection
   
   **Important**: Make sure BlueStacks is running and ADB is enabled in BlueStacks settings:
   `Settings > Advanced > Android Debug Bridge > Enable`

7. Open Docker, and open the terminal on the bottom right, and install inference-cli (don't worry the terminal isn't stuck, it takes a long time)
   ```js
   pip install inference-cli
   ```
7. Start the Inference Server
   ```js
   inference server start
   ```
8. Open http://localhost:9001/, and it should take you to the Roboflow Inference page.
9. Open BlueStacks, and open the "multi-instance manager" (should be the third icon above the Discord icon, or its in the 3 dots), and create a fresh Pie 64-bit instance.
10. Start the Pie 64-bit instance, open Google Play Store, and install Clash Royale.
11. Optional: remove the ads on the left by opening settings (gear), > Preferences > Allow BlueStacks to show Ads during gameplay (disabled)
12. Log in (or make a new) account on Clash Royale, run train.py.

**NOTE:** The bot has some minor bugs in gameplay. You can ask me any questions at the contacts page, or make contributions at the contributing page!

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

![Demo](https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExaXFtZmh1eG10amdidGhuMXBlb3dyaWZ3MjB5a2d6ZXluYXN6MTY0ZSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/SFDKIvtoRL1Og4S7fn/giphy.gif)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the project_license. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Brody Dai - itrytomakestuff99@gmail.com

Project Link: [https://github.com/krazyness/CRBot-public](https://github.com/krazyness/CRBot-public)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* [Best README Template](https://github.com/othneildrew/Best-README-Template)
* Mr. Foster, AP Computer Science teacher

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[PyTorch.org]: https://img.shields.io/badge/pytorch-green?style=for-the-badge&logo=pytorch&link=https%3A%2F%2Fpytorch.org%2F
[PyTorch-url]: https://pytorch.org
[Docker.com]: https://img.shields.io/badge/Docker-yellow?style=for-the-badge&logo=Docker&link=https%3A%2F%2Fwww.docker.com%2F
[Docker-url]: https://www.docker.com/
[Roboflow.com]: https://img.shields.io/badge/Roboflow-gray?style=for-the-badge&logo=roboflow&link=https%3A%2F%2Fwww.roboflow.com%2F
[Roboflow-url]: https://www.roboflow.com/
[Python.org]: https://img.shields.io/badge/Python-white?style=for-the-badge&logo=python&link=https%3A%2F%2Fwww.python.org%2F
[Python-url]: https://www.python.org/
