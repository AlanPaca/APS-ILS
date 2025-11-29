"""Script to seed ILS reference data into MongoDB"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path
import uuid

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# ILS Framework Data extracted from APSC
ILS_DATA = [
    # Supports Strategic Direction
    {
        "id": str(uuid.uuid4()),
        "capability_name": "Supports Strategic Direction",
        "aps_level": "APS6",
        "behaviour": "Supports shared purpose and direction",
        "description": "Understands, supports and promotes the organisation's vision, mission, and business objectives. Identifies the relationship between organisational goals and operational tasks. Clearly communicates goals and objectives to others. Understands, supports and communicates the reasons for decisions and recommendations."
    },
    {
        "id": str(uuid.uuid4()),
        "capability_name": "Supports Strategic Direction",
        "aps_level": "APS6",
        "behaviour": "Thinks strategically",
        "description": "Understands the work environment and initiates and develops team goals, strategies and work plans. Identifies broader factors, trends and influences that may impact on the team's work objectives. Considers the ramifications of issues and longer-term impact of own work and work area."
    },
    {
        "id": str(uuid.uuid4()),
        "capability_name": "Supports Strategic Direction",
        "aps_level": "APS6",
        "behaviour": "Harnesses information and opportunities",
        "description": "Gathers and investigates information from diverse sources and explores new ideas and different viewpoints. Uses experience to analyse what information is important and how it should be used. Maintains an awareness of the organisation and keeps self and others well informed on work issues and finds out about best practice approaches."
    },
    {
        "id": str(uuid.uuid4()),
        "capability_name": "Supports Strategic Direction",
        "aps_level": "APS6",
        "behaviour": "Shows judgement, intelligence and commonsense",
        "description": "Undertakes objective, systematic analysis and draws accurate conclusions based on evidence. Recognises the links between interconnected issues. Identifies problems and works to resolve them. Thinks laterally, identifies, implements and promotes improved work practices."
    },
    
    # Achieves Results
    {
        "id": str(uuid.uuid4()),
        "capability_name": "Achieves Results",
        "aps_level": "APS6",
        "behaviour": "Identifies and uses resources wisely",
        "description": "Reviews project performance and identifies opportunities for improvement. Makes effective use of individual and team capabilities and negotiates responsibility for work outcomes. Is responsive to changes in requirements."
    },
    {
        "id": str(uuid.uuid4()),
        "capability_name": "Achieves Results",
        "aps_level": "APS6",
        "behaviour": "Applies and builds professional expertise",
        "description": "Values specialist expertise and capitalises on the knowledge and skills of others within the organisation. Contributes own expertise to achieve outcomes for the business unit."
    },
    {
        "id": str(uuid.uuid4()),
        "capability_name": "Achieves Results",
        "aps_level": "APS6",
        "behaviour": "Responds positively to change",
        "description": "Establishes clear plans and timeframes for project implementation. Responds in a positive and flexible manner to change and uncertainty. Shares information with others and assists them to adapt."
    },
    {
        "id": str(uuid.uuid4()),
        "capability_name": "Achieves Results",
        "aps_level": "APS6",
        "behaviour": "Takes responsibility for managing work projects to achieve results",
        "description": "Sees projects through to completion. Monitors project progress and adjusts plans as required. Commits to achieving quality outcomes and adheres to documentation procedures. Seeks feedback from supervisor to gauge satisfaction."
    },
    
    # Supports Productive Working Relationships
    {
        "id": str(uuid.uuid4()),
        "capability_name": "Supports Productive Working Relationships",
        "aps_level": "APS6",
        "behaviour": "Nurtures internal and external relationships",
        "description": "Builds and sustains positive relationships with team members, stakeholders and clients. Proactively offers assistance for a mutually beneficial relationship. Anticipates and is responsive to client and stakeholder needs and expectations."
    },
    {
        "id": str(uuid.uuid4()),
        "capability_name": "Supports Productive Working Relationships",
        "aps_level": "APS6",
        "behaviour": "Listens to, understands and recognises the needs of others",
        "description": "Actively listens to staff, colleagues, clients and stakeholders. Involves others and recognises their contributions. Consults and shares information and ensures others are kept informed of issues. Works collaboratively and operates as an effective team member."
    },
    {
        "id": str(uuid.uuid4()),
        "capability_name": "Supports Productive Working Relationships",
        "aps_level": "APS6",
        "behaviour": "Values individual differences and diversity",
        "description": "Recognises the positive benefits that can be gained from diversity. Encourages the exploration of diverse views and harnesses the benefits of such views. Recognises the different working styles of individuals, and factors this into the management of people and tasks. Tries to see things from different perspectives. Treats people with respect and courtesy."
    },
    {
        "id": str(uuid.uuid4()),
        "capability_name": "Supports Productive Working Relationships",
        "aps_level": "APS6",
        "behaviour": "Shares learning and supports others",
        "description": "Identifies learning opportunities for others and delegates tasks effectively. Agrees clear performance standards and gives timely praise and recognition. Makes time for people and offers full support when required. Provides constructive and regular feedback. Deals with under-performance promptly."
    },
    
    # Displays Personal Drive and Integrity
    {
        "id": str(uuid.uuid4()),
        "capability_name": "Displays Personal Drive and Integrity",
        "aps_level": "APS6",
        "behaviour": "Demonstrates public service professionalism and probity",
        "description": "Adopts a principled approach and adheres to the APS Values and Code of Conduct. Acts professionally at all times and operates within the boundaries of organisational processes and legal and public policy constraints. Operates as an effective representative of the organisation in internal forums."
    },
    {
        "id": str(uuid.uuid4()),
        "capability_name": "Displays Personal Drive and Integrity",
        "aps_level": "APS6",
        "behaviour": "Engages with risk and shows personal courage",
        "description": "Provides impartial and forthright advice. Challenges issues constructively and justifies own position when challenged. Acknowledges mistakes and learns from them, and seeks guidance and advice when required."
    },
    {
        "id": str(uuid.uuid4()),
        "capability_name": "Displays Personal Drive and Integrity",
        "aps_level": "APS6",
        "behaviour": "Commits to action",
        "description": "Takes personal responsibility for meeting objectives and progressing work. Shows initiative and does what is required. Commits energy and drive to see that goals are achieved."
    },
    {
        "id": str(uuid.uuid4()),
        "capability_name": "Displays Personal Drive and Integrity",
        "aps_level": "APS6",
        "behaviour": "Promotes and adopts a positive and balanced approach to work",
        "description": "Persists with, and focuses on achieving, objectives even in difficult circumstances. Remains positive and responds to pressure in a calm manner."
    },
    {
        "id": str(uuid.uuid4()),
        "capability_name": "Displays Personal Drive and Integrity",
        "aps_level": "APS6",
        "behaviour": "Demonstrates self awareness and a commitment to personal development",
        "description": "Self-evaluates performance and seeks feedback from others. Communicates areas of strengths and acknowledges development needs. Reflects on own behaviour and recognises the impact on others. Shows commitment to learning and self-development."
    },
    
    # Communicates with Influence
    {
        "id": str(uuid.uuid4()),
        "capability_name": "Communicates with Influence",
        "aps_level": "APS6",
        "behaviour": "Communicates clearly",
        "description": "Confidently presents messages in a clear, concise and articulate manner. Focuses on key points and uses appropriate, unambiguous language. Selects the most appropriate medium for conveying information and structures written and oral communication to ensure clarity."
    },
    {
        "id": str(uuid.uuid4()),
        "capability_name": "Communicates with Influence",
        "aps_level": "APS6",
        "behaviour": "Listens, understands and adapts to audience",
        "description": "Seeks to understand the audience and tailors communication style and message accordingly. Listens carefully to others and checks to ensure their views have been understood. Checks own understanding of others' comments and does not allow misunderstandings to linger."
    },
    {
        "id": str(uuid.uuid4()),
        "capability_name": "Communicates with Influence",
        "aps_level": "APS6",
        "behaviour": "Negotiates confidently",
        "description": "Approaches negotiations with a clear understanding of key issues. Understands the desired outcomes. Anticipates and identifies relevant stakeholders' expectations and concerns. Discusses issues credibly and thoughtfully and presents persuasive counter-arguments. Encourages the support of relevant stakeholders."
    }
]

async def seed_data():
    """Seed ILS reference data into database"""
    try:
        # Check if data already exists
        count = await db.ils_reference.count_documents({})
        if count > 0:
            print(f"ILS reference data already exists ({count} documents). Skipping seed.")
            return
        
        # Insert data
        result = await db.ils_reference.insert_many(ILS_DATA)
        print(f"Successfully seeded {len(result.inserted_ids)} ILS reference documents.")
        
    except Exception as e:
        print(f"Error seeding data: {str(e)}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(seed_data())