# KICK
## KICK: Korean Football In-game Conversation State Tracking Dataset for Dialogue and Turn Level Evaluation

<img width="1210" alt="Screen Shot 2024-10-01 at 2 03 15 PM" src="https://github.com/user-attachments/assets/b368139a-7574-4a44-af6a-a021f9a8bfe1">

Recent research in dialogue state tracking has made significant progress in tracking user goals through dialogue-level and turn-level approaches, but existing research primarily focused on predicting dialogue-level belief states. In this study, we present the KICK: Korean football In-game Conversation state tracKing dataset, which introduces a conversation-based approach. This approach leverages the roles of casters and commentators within the self-contained context of sports broadcasting to examine how utterances impact the belief state at both the dialogue-level and turn-level. Toward this end, we propose a task that aims to track the states of a specific time turn and understand conversations during the entire game. The proposed dataset comprises 228 games and 2463 events over one season, with a larger number of tokens per dialogue and turn, making it more challenging than existing datasets. Experiments revealed that the roles and interactions of casters and commentators are important for improving the zero-shot state tracking performance. By better understanding role-based utterances, we identify distinct approaches to the overall game process and events at specific turns.

## Dataset Usage
```
Data
  ├── KICK_dataset.json
```
### Dataset Usage Guidelines
This dataset is made available for academic purposes and is intended for research and educational applications only. The following terms and conditions must be strictly adhered to:
- **Non-commercial Use Only :** The dataset cannot be used for any commercial purposes. This includes but is not limited to product development, commercial services, or any use where financial gain is involved.

- **Prohibition on Model Training for Commercial Use :** The dataset cannot be used for training commercial machine learning models or for any purpose where the trained models will be used in commercial applications.

- **Attribution and Intellectual Property Rights :** Proper attribution must be provided to the dataset authors and the relevant intellectual property holders. All commercial rights related to the content belong to [K-League](https://www.kleague.com/). Any derivative works or publications utilizing this dataset must acknowledge K-League as the rights holder.

- **Strict Scope of Usage :** Access to this dataset is granted under the condition that it is only used for academic research or educational purposes. The scope of usage must align with these guidelines, and any use outside of these defined boundaries is strictly prohibited.

By using this dataset, you agree to comply with these terms. Failure to adhere to these conditions may result in legal action.
## 1. Data Construction
<img width="883" alt="Screen Shot 2024-10-01 at 2 04 11 PM" src="https://github.com/user-attachments/assets/2186b30e-3922-4bfa-8d82-9e64a674951b">

### States
``` bash
DataConstruct/Kleague_crawling.py
```

The crawled data forms the states of the dataset. After each match is crawled and the relevant data is extracted, the dataset gets updated. This dataset includes the following states:
- Match Date: The date when the match occurred.
- Home/Away Team Names: Names of the teams playing the match.
- Match Events: Events such as goals, fouls, or substitutions occurring during the match, each with their respective timestamps.
- Lineups: Lists of starting and substitute players for both teams.

This script uses Selenium to crawl match data from web pages. The data includes match timelines, lineups, dates, and more, which are then stored in a CSV file. The script targets football match pages that provide a timeline of events, team names, and lineups. It uses driver.get(match_url) to open each match URL and scrape the necessary data by navigating through the HTML structure of the page. This dataset will evolve as more match URLs are crawled, enriching the overall dataset with real-time match data.


### Dialogues
``` bash
DataConstruction/clova_script.py
```
The ASR data forms the dialogues of the dataset. This script utilizes Naver Clova Speech API to perform speech-to-text processing. It takes an audio file (such as an .mp3 file) as input, processes it through the Clova Speech API, and outputs speaker-separated transcriptions in a CSV format. 

The resulting dataset from this script includes the following key attributes:

- Speaker Label: Each segment is tagged with the corresponding speaker, distinguishing who said what during the conversation.
- Text: The transcribed text for each speaker is provided.
- Time Stamps: Although empty by default, the script provides an optional time_stamp column that can be filled later for more precise segmentation.

## 2. LLM-based Inference

### Models Used

#### GPT-4o
- Model Version: gpt-4o-2024-05-13
- Model Documentation: [GPT-4o](https://platform.openai.com/docs/models/gpt-4o)
- Generation Parameters:
  - temperature: 1
  - top_p: 1

#### Gemma-2-9B-IT
- Version Info: No specific version; using the latest model as of 2024-09-25
- Model Documentation: [Gemma-2-9B-IT](https://huggingface.co/google/gemma-2-9b-it)
- Generation Parameters:
  - repetition_penalty: 1
  - temperature: 0.5
  - top_p: 0.3

#### Meta-Llama-3-8B
- Model Documentation: [Meta-Llama-3-8B](https://huggingface.co/meta-llama/Meta-Llama-3-8B)
- Generation Parameters:
  - temperature: 0.6
  - top_p: 0.3
  - max_len: 4096

### How to Run
The script to run inference using the models mentioned above is as follows. Before executing this script, it is necessary to set up each model’s API key or endpoint.

```bash
./run_inference.sh
```

## 3. Post-processing of Inference Results

Post-processing the results generated by each model to make them suitable for evaluation. The script for post-processing can be run as follows:

```bash
./run_results_process.sh
```

## 4. Evaluation

Evaluate the performance of the models using the post-processed data. Running the evaluation script will generate a log file containing various performance metrics (JGA, TGA, SA, RSA, RGI) for both the full game and the first half of the game.

```bash
./eval.sh
```

## Additional Information

This code is used to evaluate the performance of specific machine learning models and requires setting up API keys for each model before actual use. Further details about the usage of each script and the format of input files required at each stage may also be needed.

