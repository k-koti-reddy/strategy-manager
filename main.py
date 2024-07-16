import os
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import RedirectResponse
from typing import Annotated
import pymupdf
from fastapi.responses import JSONResponse
from llama_index.core import SimpleDirectoryReader
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    ServiceContext,
)
from llama_index.llms.openai import OpenAI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import markdown

app = FastAPI()

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")

def extract_text_from_pdf(file_path):
    pdf_document = pymupdf.open(file_path)
    text = ""
    for page_num in range(pdf_document.page_count):
        page = pdf_document.load_page(page_num)
        text += page.get_text()
    pdf_document.close()
    return text

def get_test_template():
    template = """
    <h1>Company Name</h1>
    {0}
    <br>
    <div class="accordion" id="accordionExample">
        <div class="accordion-item">
            <h2 class="accordion-header" id="headingOne">
                <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapseOne" aria-expanded="true" aria-controls="collapseOne">
                    <h3>Business Strategy Report</h3>
                </button>
            </h2>
            <div id="collapseOne" class="accordion-collapse collapse show" aria-labelledby="headingOne" data-bs-parent="#accordionExample">
                <div class="accordion-body">
                    <h4>Vision Statement</h4>
                    {1}
                </div>
            </div>
        </div>
    </div>
    """
    return template

def get_template():
    template = """
            <h3>Company Name</h3>
            <br>
            {0}
            <br>
            <div class="accordion" id="accordionExample">
            
                <div class="accordion-item">
                    <h2 class="accordion-header" id="headingOne">
                        <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapseOne" aria-expanded="true" aria-controls="collapseOne">
                            <h3>Business Strategy Report</h3>
                        </button>
                    </h2>
                    <div id="collapseOne" class="accordion-collapse collapse show" aria-labelledby="headingOne" data-bs-parent="#accordionExample">
                        <div class="accordion-body">
                            <h4>Vision Statement</h4>
                            {1}
                            <h4>Mission Statement</h4>
                            {2}
                            <h4>Core Values</h4>
                            {3}
                            <h4>Alignment of Company's Core Values, and Mission Statement</h4>
                            {4}
                        </div>
                    </div>
                </div>
                
                <div class="accordion-item">
                    <h2 class="accordion-header" id="headingOne">
                        <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapseOne" aria-expanded="true" aria-controls="collapseOne">
                            <h3>Company Overview</h3>
                        </button>
                    </h2>
                    <div id="collapseOne" class="accordion-collapse collapse show" aria-labelledby="headingOne" data-bs-parent="#accordionExample">
                        <div class="accordion-body">
                            <h4>Historical Background and Current Overview</h4>
                            {5}
                            <h4>SWOT Analysis</h4>
                            {6}
                            <h4>Value Chain Analysis</h4>
                            {7}
                            <h4>Business Model Canvas</h4>
                            {8}
                        </div>
                    </div>
                </div>
                
                <div class="accordion-item">
                    <h2 class="accordion-header" id="headingOne">
                        <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapseOne" aria-expanded="true" aria-controls="collapseOne">
                            <h3>Industry Analysis</h3>
                        </button>
                    </h2>
                    <div id="collapseOne" class="accordion-collapse collapse show" aria-labelledby="headingOne" data-bs-parent="#accordionExample">
                        <div class="accordion-body">
                            <h4>PORTER Five Forces Framework</h4>
                            <h5>Top five competitors</h5>
                            {9}
                            <h5>Competitive Rivalry</h5>
                            {10}
                            <h5>Threat of New Entrants</h5>
                            {11}
                            <h5>Threat of Substitutes</h5>
                            {12}
                            <h5>Bargaining Power of Suppliers</h5>
                            {13}
                            <h5>Bargaining Power of Customers</h5>
                            {14}
                            <h4>Strategies to Manage Customer Relationships</h4>
                            <h5>Strategic Priorities for company in the Next Fiscal Year Based on Five Forces Analysis</h5>
                            {15}
                            <h5>Strategic Planning for Industry Disruptions in the Aluminium Sector</h5>
                            {16}
                            <h5>Areas where the company can lead in innovation to shift competitive forces in its favour</h5>
                            {17}
                            <h4>PESTLE Analysis Framework</h4>
                            <h5>Political Factors</h5>
                            {18}
                            <h5>Economic Factors</h5>
                            {19}
                            <h5>Social Factors</h5>
                            {20}
                            <h5>Technological Factors</h5>
                            {21}
                            <h5>Environmental Factors</h5>
                            {22}
                            <h5>Legal Factors</h5>
                            {23}
                            <h4>Synthesising the Analysis</h4>
                            <h5>Overall Industry Position</h5>
                            {24}
                            <h5>External Factors Alignment</h5>
                            {25}
                            <h5>Strategic Fit and Gaps</h5>
                            {26}
                        </div>
                    </div>
                </div>
                
                <div class="accordion-item">
                    <h2 class="accordion-header" id="headingOne">
                        <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapseOne" aria-expanded="true" aria-controls="collapseOne">
                            <h3>Company Performance Analysis</h3>
                        </button>
                    </h2>
                    <div id="collapseOne" class="accordion-collapse collapse show" aria-labelledby="headingOne" data-bs-parent="#accordionExample">
                        <div class="accordion-body">
                            <h4>Value Chain Analysis Framework</h4>
                            <h5>Inbound Logistics</h5>
                            {27}
                            <h5>Operations</h5>
                            {28}
                            <h5>Outbound Logistics</h5>
                            {29}
                            <h5>Marketing and Sales</h5>
                            {30}
                            <h5>Service</h5>
                            {31}
                            <h5>Support Services</h5>
                            {32}
                            <h4>Balanced Scorecard Framework</h4>
                            <h5>Financial Perspective</h5>
                            {33}
                            <h5>Customer Perspective</h5>
                            {34}
                            <h5>Internal Process Perspective</h5>
                            {35}
                            <h5>Learning and Growth Perspective</h5>
                            {36}
                        </div>
                    </div>
                </div>

                <div class="accordion-item">
                    <h2 class="accordion-header" id="headingOne">
                        <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapseOne" aria-expanded="true" aria-controls="collapseOne">
                            <h3>Market Analysis</h3>
                        </button>
                    </h2>
                    <div id="collapseOne" class="accordion-collapse collapse show" aria-labelledby="headingOne" data-bs-parent="#accordionExample">
                        <div class="accordion-body">
                            <h4>Market Analysis</h4>
                            {37}
                            <h4>Market Segmentation and Target Customer Analysis</h4>
                            {38}
                            <h4>Blue Ocean Strategy - Identification of Untapped Markets</h4>
                            {39}
                            <h4>Competitor Analysis and Market Positioning</h4>
                            {40}
                        </div>
                    </div>
                </div>
                                
                <div class="accordion-item">
                    <h2 class="accordion-header" id="headingOne">
                        <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapseOne" aria-expanded="true" aria-controls="collapseOne">
                            <h3>Internal Capabilities and Resources</h3>
                        </button>
                    </h2>
                    <div id="collapseOne" class="accordion-collapse collapse show" aria-labelledby="headingOne" data-bs-parent="#accordionExample">
                        <div class="accordion-body">
                            <h4>VRIO Framework</h4>
                            <h5>Value</h5>
                            {41}
                            <h5>Rarity</h5>
                            {42}
                            <h5>Imitability</h5>
                            {43}
                            <h5>Organization</h5>
                            {44}
                            <h4>Resource-Based View(RBV)</h4>
                            <h5>Resource-Based View(RBV)</h5>
                            {45}
                            <h4>Strategic Opportunities and Evaluation</h4>
                            <h5>Ansoff Matrix</h5>
                            <h6>Market Penetration</h6>
                            {46}
                            <h6>Market Development</h6>
                            {47}
                            <h6>Product Development </h6>
                            {48}
                            <h6>Diversification</h6>
                            {49}
                            <h5>BCG Matrix</h5>
                            <h6>Star Products/Services</h6>
                            {50}
                            <h6>Cash Cows</h6>
                            {51}
                            <h6>Question Marks</h6>
                            {52}
                            <h6>Dogs</h6>
                            {53}
                            <h4>Regulatory Landscape</h4>
                            <h5>Government Policies and Political Factors</h5>
                            {54}
                            <h5>Economic Factors and Regulatory Requirements</h5>
                            {55}
                            <h5>Social Trends and Public Attitudes</h5>
                            {56}
                            <h5>Technological Advancements</h5>
                            {57}
                            <h5>Environmental Regulations</h5>
                            {58}
                            <h5>Legal and Regulatory Compliance</h5>
                            {59}
                        </div>
                    </div>
                </div>                                        
            </div>
    """
    return template

def get_test_questions():
    questions = ["What is the company name? Just give me the company.",
                 "What is the company's vision statement? Just give me the statements of vision"]
    return questions


def get_questions():
    questions = [
        "What is the company name? Just give me the company.",
        "What is the company's vision statement? Just give me the statements of vision",
        "What is the company's mission statement? Just give me the statements of mission",
        "What are the company's core values?",
        "How do the company's core values, vision, and mission statements align with each other?",
        "What is the company's history? How has it evolved to its current state? Give me a detailed answer.",
        "Conduct a detailed analysis of strengths, weaknesses, opportunities, and threats.",
        "Examine the company's value chain activities. Where does the company add the most value? GIve me a detailed answer",
        "Fill out the Business Model Canvas for the company. Highlight key partners, activities, resources, value propositions, customer relationships, channels, customer segments, cost structure, and revenue streams. Give a detailed answer on this",
        """Give the list of top 5 competitors of the company? if the competitors details are not present in the report, kindly give the details from your database.  Please do not mention that "there is no information about the competitors in the report" and also don't give me details of your  last update. Just give me the list of companies without giving any extra information.""",
        """How intense is the competition in the company’s industry, and what is the basis of this competition (e.g., price, quality, innovation)? Give me the detailed answer. Please include the points from the report wherever required""",
        """What barriers to entry exist for new competitors in the company's industry, and how might these barriers affect the company's position? Give me the detailed answer. Please include the points from the report wherever required.""",
        "Are there viable substitutes or alternatives to the company's products or services, and how does the company differentiate itself to minimize this threat? Give me the detailed answer. Please include the points from the report wherever required.",
        "How much power do suppliers have in the industry, and how does this impact the company's cost structure and profitability? Give me the detailed answer. Please include the points from the report wherever required.",
        "How do customers influence pricing and quality in the industry, and what strategies does the company use to manage customer relationships? Give me the detailed answer. Please include the points from the report wherever required.",
        "Based on the Five Forces analysis, what are the top three strategic priorities we should focus on in the next fiscal year?",
        "Anticipate shifts and plan for scenarios that could disrupt the current industry structure?",
        "Identify areas where the company can lead in innovation to shift competitive forces in its favour?",
        "How do government policies, trade tariffs, and political stability in the company's operational regions affect its business?  Give me the detailed answer. Please include the points from the report wherever required.",
        "What are the economic conditions (e.g., inflation, interest rates, economic growth) impacting the company's market and financial performance? Give me the detailed answer. Please include the points from the report wherever required.",
        "How do cultural trends, demographics, and consumer behaviours influence the company’s product offerings and marketing strategies? Give me the detailed answer. Please include the points from the report wherever required",
        "What technological advancements or trends are affecting the company’s operations, product development, and competitive position? Give me the detailed answer. Please include the points from the report wherever required.",
        "How do environmental issues (e.g., climate change, sustainability practices) impact the company's operations and reputation? Give me the detailed answer. Please include the points from the report wherever required.",
        "Are there any current or upcoming legal regulations (e.g., employment laws, health and safety, data protection) that the company needs to prepare for?. Give me the detailed answer. Please include the points from the report wherever required.",
        "Based on Porter's Five Forces analysis, where does the company stand in terms of industry competitiveness? Is it a leader, challenger, follower, or niche player? Give the answer in two- three lines",
        "How well does the company's strategy align with the current and forecasted external environment as revealed by the PESTLE analysis? Give the answer in two- three lines",
        "Considering both analyses, what strategic gaps (if any) are evident between the company’s current strategy and the external environment? Give me the detailed answer. Please include the points from the report wherever required.",
        "What are company's inbound logistics? How efficient are the company's supply chain and logistics operations? Are there areas where cost savings could be achieved? Give me the detailed answer. Please include the points and financials calculations from the report wherever required. Report may not contain direct data on this. Calculate the basic financial metrics and give analysis for the company. If you are not able to calculate the metric. Just mention what all metrics to be calculated and how to measure them to see best and worst. Don't mention that you are not able to calculate.",
        "Evaluate the company’s operational efficiency. Are there processes that could be optimized for better performance? Give me the detailed answer. Please include the points and financials calculations from the report wherever required. I also want you to look into balance sheet, P&L and cash flow statements and calculate important and basic metrics related to operations for the company and its analysis. Give me the numbers in table.",
        "How effective is the company at distributing its products or services to the market? Are there logistical challenges that need addressing? Give me the detailed answer. Please include the points and financials calculations from the report wherever required. I also want you to look into balance sheet, P&L and cash flow statements and calculate important and basic metrics related to operations for the company and its analysis. Give me the numbers in table.",
        "Assess the company’s marketing and sales strategies. How well do they align with customer needs and competitive dynamics?  Give me the detailed answer. Please include the points and financials calculations from the report wherever required. I also want you to look into balance sheet, P&L and cash flow statements and calculate important and basic metrics related to operations for the company and its analysis. Give me the numbers in table.",
        "Evaluate the quality of after-sales service and support. How does it impact customer satisfaction and loyalty?",
        "How do the company's support activities (Procurement, Technology Development, Human Resource Management, and Infrastructure) enhance its value proposition? Give me the detailed answer.",
        "What are the key financial metrics (e.g., revenue growth, profit margins, ROI) indicating about the company’s financial health and performance?",
        "Assume you are expert business strategy manager in the industry which company operates. How satisfied are the company’s customers? What metrics reflect this? Give me the detailed answer.if the details are not present in the report, kindly give the details from your database.  Just give me the details for this company without giving any extra information. ALso assume you are giving this information to the new recruit in strategy department in company",
        "Assume you are expert business strategy manager in the industry which company operates. ALso assume you are giving this information to the new recruit in strategy department in company.Are there internal processes that could be improved for greater efficiency or quality? Give me the detailed answer.if the details are not present in the report, kindly give the details from your database.  Just give me the details for this company without giving any extra information about you or your problems",
        "Assume you are expert business strategy manager in the industry which company operates. ALso assume you are giving this information to the new recruit in strategy department in company.How is the company investing in employee development and innovation to sustain long-term growth? Give me the detailed answer.if the details are not present in the report, kindly give the details from your database.  Just give me the details for this company without giving any extra information about you or your problems",
        """
        Based on the attached report, Give me the answers to this questions with proper headings. 
        What is the current size of the company's market? What are the projected growth rates for the company's market over the next 5 years?
        What historical growth trends are evident for the company's market?
        What are the current trends affecting the company's market?
        Are there any emerging trends that could impact the market in the near future?
        How have technological advancements impacted the company's market?
        What major opportunities exist in the market?
        What threats does the company face in the market?
        How can the company leverage opportunities and mitigate threats in this market?"
        """,
        """ 
        Based on the attached report, Give me the answers to this questions with proper headings. I dont want questions as headings
        How does the company segment its market?
        What are the characteristics of each market segment the company targets?
        Which market segments are growing the fastest?
        Who are the company's primary target customers?
        What are the key characteristics, needs, and preferences of the target customers?
        How do target customers make purchasing decisions in the company's market?
        Can you create detailed buyer personas for the company's market segments?
        What common pain points and challenges do target customers face?
        What motivates the target customers to choose the company's products or services?              
        """,
        """
        Based on the attached report, Give me the answers to this questions with proper headings. I dont want questions as headings
        What current market gaps are not being addressed by existing products or services?
        How can the company identify and capitalize on these gaps to create a blue ocean strategy?
        What are the major pain points and unmet needs of customers in the market?
        How can the company develop innovative solutions to address these pain points?
        What key factors are driving competition in the market?
        Are there any unexplored or underserved niches or sub-markets within the market?
        How can the company apply value innovation principles to create a blue ocean strategy?
        What examples of successful blue ocean strategies can be applied to the company's market?
        """,
        """
        Based on the attached report, Give me the answers to this questions with proper headings. I dont want questions as headings
        Who are the main competitors in the company's market?
        What are the strengths and weaknesses of each key competitor?
        How do the products or services of these competitors compare to the company's offerings?
        What is the market share of the key competitors?
        How intense is the competition in this market, and what are the major competitive forces?
        How are the main competitors positioned in the market?
        What are the unique selling propositions (USPs) of the top competitors?
        How can the company differentiate itself from competitors to achieve a competitive advantage?
        What strategic actions have the key competitors taken in the past year?
        What opportunities exist for a new entrant to differentiate itself in the market?
        """,
        "How valuable are the company’s resources and capabilities in enabling it to exploit opportunities and neutralize threats in the market?",
        "Which of the company’s resources and capabilities are rare or unique compared to its competitors?",
        "How easily can competitors imitate or acquire the company’s key resources and capabilities?",
        "How effectively is the company organized to exploit its valuable, rare, and difficult-to-imitate resources and capabilities?",
        "What specific resources and capabilities give the company a competitive advantage in its industry?",
        "What strategies can the company pursue to increase its market share within existing markets using current products or services? Give me the detailed answer based on the report attached",
        "Are there new markets (geographical or demographic) that the company can enter with its existing products or services? Give me the detailed answer based on the report attached",
        "What new products or services can the company develop to meet evolving market needs or technological trends within its current markets? Give me the detailed answer based on the report attached",
        "Is diversifying into new markets with new products or services a viable strategy for the company? What are the potential benefits and risks?  Give me the detailed answer based on the report attached",
        "Which of the company’s products or services have high market growth and high market share? How can the company capitalize on these? Give me the detailed answer based on the report attached? Give me the Strategies to Capitalize on High Market Growth and High Market Share",
        "Which products or services have low market growth but high market share, and how can the company use the revenue from these to fund other segments? Give me the detailed answer based on the report attached? Give me the Strategies to Capitalize on Cash Cows",
        "Identify products or services with high market growth but low market share. What strategies could convert these into Stars or should they be divested? Give me the detailed answer based on the report attached?",
        "Are there products or services with low market growth and low market share that should be discontinued or repositioned?Give me the detailed answer based on the report attached?",
        """Based on the attached report, Give me the answers to this questions with proper headings. I dont want questions as headings. DOnt give me conclusions. What government policies and political factors affect the company’s regulatory environment? Are there any upcoming political changes that could impact the company’s operations?""",
        "Based on the attached report, Give me the answers to this questions with proper headings. I dont want questions as headings. DOnt give me conclusions. How do economic factors, such as inflation and economic growth, influence regulatory requirements? What economic policies affect the company’s industry?",
        "Based on the attached report, Give me the answers to this questions with proper headings. I dont want questions as headings. Dont give me conclusions. How do social trends and public attitudes impact regulatory standards and compliance requirements?Are there any social issues that the company must address through its compliance programs?",
        "Based on the attached report, Give me the answers to this questions with proper headings. I dont want questions as headings. Dont give me conclusions. What technological advancements impact the regulatory landscape for the company? How is the company adapting to regulatory changes related to new technologies?",
        "Based on the attached report, Give me the answers to this questions with proper headings. I dont want questions as headings. Dont give me conclusions. What environmental regulations affect the company’s operations?How does the company comply with environmental standards and sustainability requirements?",
        "Based on the attached report, Give me the answers to this questions with proper headings. I dont want questions as headings. Dont give me conclusions. What specific laws and regulations govern the company’s industry?How does the company stay updated on legal changes and ensure compliance?"
    ]
    return questions
            
@app.post("/uploadfile/")
async def create_upload_file(businessName: Annotated[str, Form()], annualReport: UploadFile):
    if not annualReport:
        return {"message": "No upload file sent"}
    else:
        try:
            # Save the uploaded PDF temporarily (optional)
            with open("temp.pdf", "wb") as temp_file:
                temp_file.write(await annualReport.read())
                
            print(businessName)
            
            # Create Query Engine
            llm = OpenAI(model="gpt-4o")
            # create service context
            service_context = ServiceContext.from_defaults(llm=llm)
            documents = SimpleDirectoryReader(input_dir=".").load_data()
            print('create index')
            index = VectorStoreIndex.from_documents(documents, service_context=service_context)
            print('create query engine')
            query_engine = index.as_query_engine()
            print('query engine created')
            
            questions = get_questions()
            
            print('populate questions completed')
            
            template = get_template()
            
            print('populate template completed')
            answers = []
            for question in questions:
                response = query_engine.query(question)
                html = markdown.markdown(str(response))
                answers.append(html)

            html = template.format(*answers)
            os.remove("temp.pdf")
            
        except Exception as e:
            return JSONResponse(content={"error": f"Error processing PDF: {str(e)}"}, status_code=500)
    
        return {"html": html}
