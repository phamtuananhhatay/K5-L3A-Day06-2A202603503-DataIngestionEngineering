# 10 mẫu coherence để học viên chấm

**Cập nhật:** Phạm Tuấn Anh đã gửi điểm và lý do cho đủ 10 mẫu. Xem
[báo cáo kết quả](coherence_review_student.md). Phần “chưa có điểm” bên dưới mô tả
trạng thái khi chuẩn bị mẫu; nội dung chunk và vị trí nguồn được giữ nguyên.

Chưa có điểm. Chọn 10 trang đầu corpus theo thứ tự tăng dần; mỗi trang lấy điểm bắt đầu đoạn văn chính được ghi bằng anchor bên dưới. Chọn trước khi nhận điểm coherence, không chọn theo kết quả chấm. Nội dung đã từng được dùng trong pipeline/dev nên không coi đây là chọn mù.

Nếu nhiều chunk bao phủ điểm nguồn, chọn chunk có start_char nhỏ nhất. Offset bắt đầu từ 0, cuối loại trừ. C dùng đúng chunk B; có thể dùng cùng điểm nếu bạn xác nhận.

**Thang điểm:** 0 = bị cắt/thiếu chủ thể làm khó hiểu; 1 = hiểu một phần nhưng thiếu ngữ cảnh; 2 = tự hiểu và giữ trọn ý. Chấm nội dung thực tế, không chấm theo việc trả lời câu hỏi benchmark.

## Mẫu 01 — PDF 23 (trang in 15)

Section: Energy Data

Vị trí nguồn: ký tự 15, bắt đầu bằng **Although the world**.

<details>
<summary>Xem toàn bộ văn bản trang nguồn để đối chiếu</summary>

```text
15
Energy Data
Although the world has made important gains toward
SDG 7, efforts have been falling well short of the scale
required to reach the SDG 7 targets (see Box 2.1) by 2030.
This has only been exacerbated by the COVID-19 crisis,
which is having a serious effect on SDG 7 progress. At
the same time, the pandemic has pointed to the urgent
need for access to reliable, affordable, sustainable, and
modern energy—for hospitals and health facilities to treat
patients, for schools to prepare children for the digital
economy, for communities to pump clean water, and for
people to gain access to information. The full impact of
the crisis is yet to become clear. Over the coming years,
more data on the crisis impact to progress toward SDG 7
will become available.
The core work of ESMAP’s Data and Analytics Hub is now
more relevant than ever, as the hub has the capacity
to assess the impact of COVID-19 on energy access,
renewables, and energy efficiency. The hub also assesses
energy-related needs in the pandemic response and
rebuilding efforts. Analytic support to assess the current
and potential electricity demand will help clients and
World Bank teams to respond to end-user needs and push
productive use efforts successfully.
The Data and Analytics Hub draws from lessons learned
over time with the implementation of ESMAP’s programs,
including the importance of: (1) engaging operational
energy teams, governments, and development partners
in the countries where data are collected; (2) enhancing
capacity building to collect data sustainably and apply
findings more effectively to policymaking; (3) making
methodology more transparent, critical to ensure
credibility of the data; and (4) fostering collaboration
between agencies to enable more effective dissemination.
ENERGY DATA AND ANALYTICS HUB
Data and analytics are key elements for evidence-based
decision making on policies and investments necessary for
achieving SDG 7. However, comprehensive, detailed data at
the global, national, and regional levels for energy access
(electricity and cooking solutions) is lacking. Geospatial
information gaps are a barrier to electrification planning,
and more efficient ways to collect data on energy access
are required to support scaled-up investment.
The ESMAP Energy Data and Analytics Hub aims to be an
all-inclusive data and knowledge platform that offers a
free, unique breadth of energy-related information to use.
The hub manages several energy data platforms, as well as
four synergetic products—Tracking SDG 7, the Multi-Tier
Framework, RISE, and Energy Demand Estimation—that
track SDG 7.
150
million
The electricity access rate, in access-deficit countries,
must increase from 82% in 2019 to 94% by 2025 to
achieve 100% access by 2030. This means a yearly
gain of two percentage points, or electrification being
brought to about 150 million people between now
and 2025. This represents a 33% increase: an extra
0.5 percentage points or additional 40 million people
per year over the current rate of progress.
```

</details>

### A — 500 ký tự

Chunk ID: `62fac5be36fdaf8f86c1a5f6ac25db03a71f870189dd4a04bef9cd7e5a192c7f`

```text
15
Energy Data
Although the world has made important gains toward
SDG 7, efforts have been falling well short of the scale
required to reach the SDG 7 targets (see Box 2.1) by 2030.
This has only been exacerbated by the COVID-19 crisis,
which is having a serious effect on SDG 7 progress. At
the same time, the pandemic has pointed to the urgent
need for access to reliable, affordable, sustainable, and
modern energy—for hospitals and health facilities to treat
patients, for schools to prepare chil
```

### B — 288 ký tự

Chunk ID: `33c5adbbfc1d0c3ac4e74e172b062ede4d6eb3cca0720ea3a525d8e2a68814f0`

```text
15
Energy Data
Although the world has made important gains toward
SDG 7, efforts have been falling well short of the scale
required to reach the SDG 7 targets (see Box 2.1) by 2030.
This has only been exacerbated by the COVID-19 crisis,
which is having a serious effect on SDG 7 progress.
```

**Bạn gửi vào chat:**
`Mẫu 01: A=..., B=..., C=...; lý do A: ...; lý do B/C: ...`

## Mẫu 02 — PDF 24 (trang in 16)

Section: Energy Data

Vị trí nguồn: ký tự 59, bắt đầu bằng **SDG 7 is one**.

<details>
<summary>Xem toàn bộ văn bản trang nguồn để đối chiếu</summary>

```text
16
ESMAP Annual Report 2021
SUSTAINABLE DEVELOPMENT GOAL 7
SDG 7 is one of the 17 Sustainable Development Goals established by the United
Nations General Assembly in 2015. It aims to “[e]nsure access to affordable,
reliable, sustainable and modern energy for all.” The goal has five targets, to be
achieved by 2030:
Target 7.1: Universal access to modern energy. This target has two indicators:
• Indicator 7.1.1: Proportion of population with access to electricity.
• Indicator 7.1.2: Proportion of population with primary reliance on clean fuels and technology.
Target 7.2: Increase global percentage of renewable energy.
Target 7.3: Double the improvement in energy efficiency.
• Target 7.A: Promote access to research, technology and investments in clean energy.
• Target 7.B: Expand and upgrade energy services for developing countries.
EnergyData.info. EnergyData.info is an open data
platform providing easy, free access to data and
analytics relevant to the energy sector. This platform
serves as a public good available to governments,
development organizations, the private sector,
nongovernmental organizations, academia, civil
society organizations, and individuals to share data
and analytics that can complement ESMAP data to
help achieve SDG 7 targets. ESMAP is also developing
web-based GIS visualization applications hosted on
the EnergyData.info platform that are used by Bank
teams and external stakeholders for making informed
decisions and developing effective projects.
Tracking SDG 7: Energy Progress Report. The report is
a comprehensive tool that tracks 220 countries’ progress
toward achieving the SDG 7 energy pillars on access to
electricity, clean cooking, renewables, and efficiency. It is
jointly produced every year by the five SDG 7 custodian
agencies, namely the World Bank/ESMAP, the International
Energy Agency (IEA), the International Renewable Energy
Agency (IRENA), the United Nations Statistics Division
(UNSD), and WHO, with the support of the SDG 7 Technical
Advisory Group at the UN. As the custodian agency for
SDG 7.1.1, the World Bank/ESMAP is responsible for the
electrification data and the chapter on access to electricity.
In FY2021, the ESMAP team introduced the notions of
affordability, availability, and reliability to the tracking. The
seventh edition of the report was published in June 2021; it
found that a greater share of the global population gained
access to electricity than ever before, but the number of
people without electricity in Sub-Saharan Africa increased.
According to the report, the number of people without
access to electricity declined globally from 1.2 billion in
2010 to 759 million in 2019. However, under current and
planned policies, plus the effects of the COVID-19 crisis,
an estimated 660 million people would still lack access in
2030, most of them in Sub-Saharan Africa.
Multi-Tier Energy Access Tracking Framework. The
Multi-Tier Framework (MTF) is a tool that identifies
and analyzes on a country level the main reasons that
households are not using electricity, or that their use
is limited, and then recommends a set of measures to
remove the identified constraints. By going beyond the
traditional binary measure of “connected or not connected”
BOX 2.1
```

</details>

### A — 499 ký tự

Chunk ID: `170b658bb340b64f84d4b2baeaacba09d46e5bef5d5333c73b07b88c31f884ea`

```text
16
ESMAP Annual Report 2021
SUSTAINABLE DEVELOPMENT GOAL 7
SDG 7 is one of the 17 Sustainable Development Goals established by the United
Nations General Assembly in 2015. It aims to “[e]nsure access to affordable,
reliable, sustainable and modern energy for all.” The goal has five targets, to be
achieved by 2030:
Target 7.1: Universal access to modern energy. This target has two indicators:
• Indicator 7.1.1: Proportion of population with access to electricity.
• Indicator 7.1.2: Proportion of
```

### B — 362 ký tự

Chunk ID: `b57b2ebce8e46b8127b82fed59044997409229c8291057b73c547773810f8f5a`

```text
16
ESMAP Annual Report 2021
SUSTAINABLE DEVELOPMENT GOAL 7
SDG 7 is one of the 17 Sustainable Development Goals established by the United
Nations General Assembly in 2015. It aims to “[e]nsure access to affordable,
reliable, sustainable and modern energy for all.” The goal has five targets, to be
achieved by 2030:
Target 7.1: Universal access to modern energy.
```

**Bạn gửi vào chat:**
`Mẫu 02: A=..., B=..., C=...; lý do A: ...; lý do B/C: ...`

## Mẫu 03 — PDF 25 (trang in 17)

Section: Energy Data

Vị trí nguồn: ký tự 488, bắt đầu bằng **RISE is the first**.

<details>
<summary>Xem toàn bộ văn bản trang nguồn để đối chiếu</summary>

```text
17
Energy Data
for electricity access and “solid versus nonsolid fuels” for
cooking, the framework provides more accurate data on
the actual services households received. The MTF is a
complementary source for tracking SDG 7, helping inform
policy and investment decisions concerning access. Since
its creation in 2015, the MTF has collected data from 21
countries. In FY2021, MTF country reports on Nigeria and
Liberia were published.
Regulatory Indicators for Sustainable Energy (RISE).
RISE is the first global scorecard that captures the policies
and regulations in place to facilitate progress on SDG 7.
RISE is published biannually and is available free on an
online data platform (rise.esmap.org) that enables users
to customize the information they need on each country’s
power sector and regulatory and policy framework.
RISE indicators are included in the outputs of several
well-established global initiatives, including the REN21
Renewables Global Status Report, Clean Cooking Alliance
Communication Corps, and SDG 7 policy briefs compiled
by the multi-stakeholder SDG 7 Technical Advisory Group.
The third edition of RISE “RISE 2020: Sustaining the
Momentum” was launched in December 2020 and includes
138 countries, 32 indicators and more than 160 questions.
This edition tracks for the first-time clean cooking policy
and regulations pillar in more than fifty countries. RISE
indicators informed countries on policy best practices
and provided framework to sustainable energy policy
pathways. RISE outputs were used to track progress of
several ESMAP grants and World Bank projects, including,
among other, the ECA Sustainable Heating Program,
Western Balkans Energy Transition Program, Haiti
Electricity Access and Sustainable Resilient and Inclusive
Development of the Energy Sector, Haiti Renewable Energy
for All Project.
The Global Electricity Regulatory Index (GERI). The
index is a companion piece to the RISE scorecard and is
jointly produced by the African Development Bank and the
World Bank. GERI collects data from over 100 developing
countries to track the gaps between regulation and actual
implementation. This enables users to identify gaps in
their country’s regulatory framework and benchmark their
performance against global peers.
Electricity Demand Estimation. The Electricity Demand
Estimation program supports World Bank operations in
using reliable and transparent estimation tools and data
for the residential and agricultural customer segments of
electrification strategy.
In FY2021, the Energy Data and Analytics Hub’s products
and database informed more than 30 lending or research
projects. Out of the 33 energy and extractives operations
approved in that fiscal year, 11 of them used the hub as
an informative resource; all grant proposals submitted
to ESMAP in FY2021 indicated that they have used the
Knowledge Hub products to inform the advisory and
analytical products.
For example, in its project on promoting access and
transition to clean energy in the Sahel, the World Bank
team used Tracking SDG 7 data extensively to engage client
countries in dialogue on how to push the SDG 7 agenda
forward in the region.
Similarly, the MTF informed the implementation of the
World Bank project on solar energy in local communities
in Burundi. The project seeks to expand access to
energy services in rural areas of the country, and the
MTF provided detailed information on the energy access
situation of households, including quantity and quality of
services.
In Mozambique, the Electricity Demand Estimation
program supported the preparation of an energy access
project, helping to illuminate the potential demand from
the irrigation sector and the optimal energy solutions.
Photo © Volkovslava/Shutterstock
```

</details>

### A — 499 ký tự

Chunk ID: `d6f0721f1e74cd64a3713149f4de092126281edd37d7cab773ad5fec6301d644`

```text
17
Energy Data
for electricity access and “solid versus nonsolid fuels” for
cooking, the framework provides more accurate data on
the actual services households received. The MTF is a
complementary source for tracking SDG 7, helping inform
policy and investment decisions concerning access. Since
its creation in 2015, the MTF has collected data from 21
countries. In FY2021, MTF country reports on Nigeria and
Liberia were published.
Regulatory Indicators for Sustainable Energy (RISE).
RISE is the
```

### B — 340 ký tự

Chunk ID: `dc5d3674ef6ce19c0d7fba7ad17b2e24f800a01949ac7e6665bb174d700a2bee`

```text
RISE is the first global scorecard that captures the policies
and regulations in place to facilitate progress on SDG 7.
RISE is published biannually and is available free on an
online data platform (rise.esmap.org) that enables users
to customize the information they need on each country’s
power sector and regulatory and policy framework.
```

**Bạn gửi vào chat:**
`Mẫu 03: A=..., B=..., C=...; lý do A: ...; lý do B/C: ...`

## Mẫu 04 — PDF 27 (trang in 19)

Section: Foundations of Energy Transition

Vị trí nguồn: ký tự 36, bắt đầu bằng **The world must**.

<details>
<summary>Xem toàn bộ văn bản trang nguồn để đối chiếu</summary>

```text
19
Foundations of Energy Transition
The world must use the opportunity today to move rapidly
to a decarbonized energy sector taking advantage of
the plummeting cost of renewable sources of energy;
technological advances in demand management, storage,
and digitalization; and new decentralized business models
for service delivery. The energy transition will need to be
based on renewables and efficient technologies as the
breakdown of electricity generation by source (see Figure
2.1) in a Paris Agreement-compatible scenario (IRENA 2019).
However, achieving these targets by using existing ways
of doing business is not an option, and new, innovative
regulations, policies, and markets need to be deployed.
The energy transition should also ensure that its
socioeconomic impacts are positive and equitable, such as
improved gender balance in the energy sector.
A foundation for energy transition lies in a well-functioning,
financially sound power sector. Therefore, ESMAP—
through its overarching Foundation for Energy Transition
program—takes on the challenge of gluing together
various ESMAP programs and providing a comprehensive
policy framework for the energy transition by employing
innovative solutions in five interlinked areas:
1. Designing new business and regulatory models for
utilities for the future, able to maintain financial
viability and service standards (Utilities for the Energy
Transition program)
2. Developing competitive markets, connecting regions,
and deploying power trade mechanisms that provide
the price signals and incentives needed to induce the
investment in the right technologies and behaviors
(Markets, Connectivity and Trade program)
3. Helping countries to stop subsidizing fossil fuels
and remove subsidies and other distortions (Energy
Subsidy Reform Facility)
4. Supporting transitioning from coal and least-cost
planning (Supporting Coal Regions in Transition)
5. Promoting gender equality in the energy sector
(Closing Gender Gaps in Energy)
UTILITIES FOR ENERGY
TRANSITION
The energy sector is under transformation, driven by
decarbonization goals and technological advancements
that are challenging the traditional modus operandi of
utilities and the adequacy of existing regulations. The
increasing availability of cost-effective digital technologies
is opening new opportunities for enhanced data-driven
decision making, automation, and new business models
that can help improve the flexibility and reliability of the
grid. This is critical for the higher penetration of variable
renewable energy, distributed energy resources, and the
clean energy transition.
The Utilities for Energy Transition program supports
utilities that are grappling with this changing landscape.
The program provides technical assistance and pilot
programs to guide utilities’ investments in digital and
decentralized technologies, such as advanced metering
infrastructure, and grid-connected distributed energy
resources. In FY2021, the program focused on bolstering
an enabling environment, including regulatory frameworks
to put in place appropriate incentives for the investment in
34
%
Coal is still the world’s most dominant energy
source, generating 34 percent of global electricity
in 2020. There is approximately 2,000 GW of coal-
based generation capacity remaining worldwide,
despite widespread recognition of coal’s strong
negative impact on climate change.
```

</details>

### A — 500 ký tự

Chunk ID: `9462a840e7f91713e7df842195aebe0c655cc55296a714b3d955e140feec7652`

```text
19
Foundations of Energy Transition
The world must use the opportunity today to move rapidly
to a decarbonized energy sector taking advantage of
the plummeting cost of renewable sources of energy;
technological advances in demand management, storage,
and digitalization; and new decentralized business models
for service delivery. The energy transition will need to be
based on renewables and efficient technologies as the
breakdown of electricity generation by source (see Figure
2.1) in a Paris Agr
```

### B — 330 ký tự

Chunk ID: `3a6404f7a37c0e893a3dae3e42d1b25f21b4184a6919be551df512c4f7d107cc`

```text
19
Foundations of Energy Transition
The world must use the opportunity today to move rapidly
to a decarbonized energy sector taking advantage of
the plummeting cost of renewable sources of energy;
technological advances in demand management, storage,
and digitalization; and new decentralized business models
for service delivery.
```

**Bạn gửi vào chat:**
`Mẫu 04: A=..., B=..., C=...; lý do A: ...; lý do B/C: ...`

## Mẫu 05 — PDF 28 (trang in 20)

Section: Foundations of Energy Transition

Vị trí nguồn: ký tự 128, bắt đầu bằng **In Kenya, for example**.

<details>
<summary>Xem toàn bộ văn bản trang nguồn để đối chiếu</summary>

```text
20
ESMAP Annual Report 2021
such technologies, the emergence of decentralized energy
resources, and associated business models.
In Kenya, for example, which implemented an expansive
electrification project, as well as in Niger, the Utilities for
Energy Transition program provided support with studies
on electricity demand. The program leveraged utility data
and piloted options for appliance finance and distribution
to make demand-stimulating appliances affordable to
consumers, in collaboration with ESMAP’s Innovative
Financing for Access program.
ELECTRICITY MARKETS, GRID
CONNECTIVITY , AND REGIONAL
TRADE
Well-functioning electricity markets—able to provide
efficient price signals to guide dispatch and inform
investment—are needed to stimulate the appropriate
and timely investment required to achieve low-carbon
and electricity security goals at least cost and, as such,
facilitate and support achievement of the SDG 7 targets.
The situation is becoming especially acute at the time
when the world is undergoing an accelerated energy
transition, driven by rapidly changing technological,
environmental, and economic factors. These include
falling costs of renewables, leading to their progressive
adoption; the decentralization of generation, propelled by
the growing availability and reduced costs of distributed
energy resources; and changes in the responsiveness of
demand, enabled by the advancement of information
and communication technologies (electric vehicles, smart
metering, digitalization) and socioeconomic transformation
(urbanization, industrialization).
The Electricity Markets, Grid Connectivity and Regional
Trade (MARCOT) program is one of the newest windows
of ESMAP. Establishing the MARCOT program reflects the
desire, from several angles—from the client countries,
from the Bank management, and from the ESMAP
donors—to systematize vast knowledge of the Bank’s
engagement in the area of power market reforms, set
up a consolidated center of expertise on power market
solutions tailored to the changing environment and client
countries’ evolving needs, and provide a practical platform
Figure 2.1. Electricity Generation by Source, 2019
Source: Innovation landscape for a renewable-powered future: Solutions to integrate variable renewables, IRENA, 2019.
Electricity Generation (TWh/yr)
0
20,000
30,000 85%
Renewables
Non-Renewables
Renewables
Non-Renewables
15%
40,000
2015
Others (incl. marine and hybrid)
2015–2050
Changes
2050
REmap Case
50,000
24%
76%
Geothermal Wind CSP Solar PV Bioenergy
Hydropower Nuclear Natural Gas Oil Coal
```

</details>

### A — 500 ký tự

Chunk ID: `a858fc76b68d8b8a92511943ab1272e434c68a846b42b90d39df320359ca5ec9`

```text
20
ESMAP Annual Report 2021
such technologies, the emergence of decentralized energy
resources, and associated business models.
In Kenya, for example, which implemented an expansive
electrification project, as well as in Niger, the Utilities for
Energy Transition program provided support with studies
on electricity demand. The program leveraged utility data
and piloted options for appliance finance and distribution
to make demand-stimulating appliances affordable to
consumers, in collaboration w
```

### B — 324 ký tự

Chunk ID: `1cc9260f1eb5248c446729828c9ac7a85ab454414e25327b93bf4b3330e022b1`

```text
20
ESMAP Annual Report 2021
such technologies, the emergence of decentralized energy
resources, and associated business models.
In Kenya, for example, which implemented an expansive
electrification project, as well as in Niger, the Utilities for
Energy Transition program provided support with studies
on electricity demand.
```

**Bạn gửi vào chat:**
`Mẫu 05: A=..., B=..., C=...; lý do A: ...; lý do B/C: ...`

## Mẫu 06 — PDF 29 (trang in 21)

Section: Foundations of Energy Transition

Vị trí nguồn: ký tự 163, bắt đầu bằng **In FY2021, the MARCOT program**.

<details>
<summary>Xem toàn bộ văn bản trang nguồn để đối chiếu</summary>

```text
21
Foundations of Energy Transition
for implementing recommendations from the Bank’s
2019 flagship report Rethinking Power Sector Reforms in the
Developing World.
In FY2021, the MARCOT program allocated technical
assistance grants to a total of 16 activities in all the regions
the World Bank serves (except EAP), focusing on strategic
objectives of increasing the number of countries with: (1)
established or improved markets for energy services; (2)
interconnected grids and increased regional trade; and (3)
increased financing from the public and private sources.
The program teamed up with the RISE team to establish
a comprehensive, regularly updated database of power
markets globally. The database holds information
about the electricity sector/market characteristics and
development over time, presenting a completely new and
unique offering for benchmarking the performance of
developing markets.
The MARCOT program also launched a series of formal
training courses on the “Fundamentals of Energy Markets.”
ENERGY SUBSIDY REFORM FACILITY
Established in 2013, ESMAP’s Energy Subsidy Reform
Facility (ESRF) supports governments in the design and
implementation of energy subsidy reform programs. The
facility supports analytic work on various aspects of the
complex energy subsidy reform agenda, including poverty,
social protection, fiscal management, macroeconomics,
political economy, communication, and climate change
mitigation.
There is growing recognition of the need to reform fossil
fuel subsidies in view of their climate impact, significant
fiscal cost, and the economic distortions they create. With
global cumulative subsidy spending in 2020 estimated at
$180 billion, per IEA figures, energy subsidies impose a
heavy burden on governments and taxpayers, and divert
limited government resources away from critical priorities.
These priorities include recovery from the global pandemic,
investments in green infrastructure, and strengthening
service delivery in health and education.
Reflecting the global recognition of the importance of
subsidy reform and the complex challenges that need to
UZBEKISTAN
FINANCIAL ANALYSIS OF THE
NATIONAL GRID
In Uzbekistan, an in-depth study of the National Electric Grid of Uzbekistan (NEGU), sponsored by
ESRF, provided a comprehensive analysis of NEGU’s financial performance and of key risks to the
company’s financial sustainability. The study contributed to the government of Uzbekistan’s decision
to initiate action to improve NEGU’s financial sustainability. The study also promoted the design of
the World Bank’s Electricity Sector Transformation and Resilient Transmission project, a $472 million
operation approved in FY2021 that will improve the performance of NEGU and supply reliable energy to
millions of households and businesses across the country.
BOX 2.2
```

</details>

### A — 500 ký tự

Chunk ID: `9543d9c032ac1ed981617d8cb0f7783ca35f9fbe36a98dc72ffecd63753f3b28`

```text
21
Foundations of Energy Transition
for implementing recommendations from the Bank’s
2019 flagship report Rethinking Power Sector Reforms in the
Developing World.
In FY2021, the MARCOT program allocated technical
assistance grants to a total of 16 activities in all the regions
the World Bank serves (except EAP), focusing on strategic
objectives of increasing the number of countries with: (1)
established or improved markets for energy services; (2)
interconnected grids and increased regional trad
```

### B — 404 ký tự

Chunk ID: `76ffa25cf3d659bb864a5d6932da3ac1faaf611ef81e997008e63140ec8d5e81`

```text
In FY2021, the MARCOT program allocated technical
assistance grants to a total of 16 activities in all the regions
the World Bank serves (except EAP), focusing on strategic
objectives of increasing the number of countries with: (1)
established or improved markets for energy services; (2)
interconnected grids and increased regional trade; and (3)
increased financing from the public and private sources.
```

**Bạn gửi vào chat:**
`Mẫu 06: A=..., B=..., C=...; lý do A: ...; lý do B/C: ...`

## Mẫu 07 — PDF 30 (trang in 22)

Section: Foundations of Energy Transition

Vị trí nguồn: ký tự 61, bắt đầu bằng **In Sudan, the Energy**.

<details>
<summary>Xem toàn bộ văn bản trang nguồn để đối chiếu</summary>

```text
22
ESMAP Annual Report 2021
SUDAN
ELIMINATING FUEL SUBSIDIES
In Sudan, the Energy Sector Recovery Technical Assistance program, a $2 million multi-donor
program, was established in 2019 to support the government with energy subsidy reform, clean energy
transition, and increasing access to energy. An ESMAP-funded policy paper prepared as a part of the
program identified energy subsidies as a major driver of the local economic crisis and showed that
savings from successful reforms can deliver positive impacts for the public and improve the fiscal
sustainability of Sudan. Since October 2020, the government of Sudan carried out several reforms to
eliminate subsidies for gasoline and diesel products, which effectively ended all subsidies for these
products by June 2021. These favorable reforms have also contributed to Sudan’s clearing its arrears
to the International Development Association (IDA), enabling its full reengagement with the World
Bank Group after nearly three decades and paving the way for the country to access nearly $2 billion
in IDA grants for poverty reduction and sustainable economic recovery.
BOX 2.3
Photo © Eugene Kim
be tackled by client countries, ESRF has seen strong and
growing demand from World Bank teams supporting
client countries in their efforts for energy subsidy reform.
Between FY14, when the first grants were made, and
FY2021, the facility allocated $24.6 million for technical
assistance that aided client governments in the design and
delivery of energy subsidy reform in 65 countries.
In FY2021, ESRF provided $2.5 million in country grants
toward reforming energy subsidies, bringing the total
to 35 active grants under implementation. In addition
to informing policy on the ground, ESRF-funded grants
informed the design of several World Bank projects
approved in FY2021, totaling $4.2 billion.
```

</details>

### A — 500 ký tự

Chunk ID: `e6e7a1a2f2a3cf7fb1dd7c52aa2f92a48ea767b77703f8d1fa100319ddd85ad7`

```text
22
ESMAP Annual Report 2021
SUDAN
ELIMINATING FUEL SUBSIDIES
In Sudan, the Energy Sector Recovery Technical Assistance program, a $2 million multi-donor
program, was established in 2019 to support the government with energy subsidy reform, clean energy
transition, and increasing access to energy. An ESMAP-funded policy paper prepared as a part of the
program identified energy subsidies as a major driver of the local economic crisis and showed that
savings from successful reforms can deliver posi
```

### B — 297 ký tự

Chunk ID: `0df2b978a7e54c9512ed5ae57cc3d5f81458aff171b861b9722ddb1b07fbdd6b`

```text
22
ESMAP Annual Report 2021
SUDAN
ELIMINATING FUEL SUBSIDIES
In Sudan, the Energy Sector Recovery Technical Assistance program, a $2 million multi-donor
program, was established in 2019 to support the government with energy subsidy reform, clean energy
transition, and increasing access to energy.
```

**Bạn gửi vào chat:**
`Mẫu 07: A=..., B=..., C=...; lý do A: ...; lý do B/C: ...`

## Mẫu 08 — PDF 31 (trang in 23)

Section: Foundations of Energy Transition

Vị trí nguồn: ký tự 36, bắt đầu bằng **The outcomes achieved**.

<details>
<summary>Xem toàn bộ văn bản trang nguồn để đối chiếu</summary>

```text
23
Foundations of Energy Transition
The outcomes achieved under the country grants were
complemented by the facility’s own knowledge work. In
December 2020, ESRF hosted its first virtual knowledge
forum for World Bank staff. The forum included a
comprehensive debate on the challenges of energy
subsidy reforms during and after the pandemic, as well
as knowledge exchange among diverse stakeholders,
including subject experts and government representatives.
SUPPORTING COAL REGIONS IN
TRANSITION
Coal is the world’s most dominant energy source,
generating 34 percent of global electricity in 2020.
Although the pandemic drove a drop in coal demand of
220 million tons of coal equivalent (Mtce), or 4 percent, in
many countries, coal consumption is on the rise and coal
remains the cheapest and most profitable energy source.
The World Bank Group stopped the direct financing of new
utility-scale coal-fired power projects in 2010. The World
Bank supports national, regional, and local authorities in
developing clear roadmaps for the transition, focusing
on governance structures, the welfare of people and
communities, and the remediation and repurposing of
former mining lands and coal-fired power plants.
Following the World Bank’s seminal report Managing Coal
Mine Closure: Achieving a Just Transition for All in 2018, with
lessons from 11 former World Bank investment projects
on coal sector transition alongside new evidence from
four coal transitioning countries (China, the Netherlands,
the UK, and the US), the World Bank is now finalizing
a comprehensive set of global coal mine closure good
practice technical standards. These standards will
enable the transition from “physical closure” to a more
“sustainable closure” in the context of achieving a “just
transition for all.”
A key priority is to support countries and communities
most affected by the phasing out of coal as they transition
to cleaner energy sources. ESMAP supports coal mine
closure and coal plant repurposing, particularly through
partnerships like the Platform Initiative in Support of Coal
Regions in Transition for Western Balkans and Ukraine,
which was launched in December 2020. As part of this
effort, the new program on Supporting Coal Regions
in Transition also assists client countries that have
made the decision to transition from coal in developing
roadmaps for transition. Technical assistance to support
a just energy transition has commenced in Bosnia and
Herzegovina and Ukraine. In the two countries, ESMAP is
supporting the development of roadmaps for transition
using the 3*3 Assessment Framework, developed by the
World Bank team.
The program also designed twinning activities between
Polish and Ukrainian coal regions, and the first study
tour took place in early March 2021 in virtual mode due
to COVID-19-related restrictions. Formal trainings are
delivered via the Coal Regions in Transition Learning
Academy, which is led by the College of Europe in Natolin,
Warsaw, and the World Bank, with support from the
European Commission. An online virtual delivery of a first
set of learning modules was finalized in September 2021.
South Africa is the largest producer of coal in Africa and
one of the largest coal producers in the world. Its state
power utility produces 95 percent of the nation’s electricity,
the bulk of this coming from coal-fired capacity. Five
million dollars in Technical Assistance was mobilized by
ESMAP for the coal retirement and repurposing agenda
from the UK Department for Business, Energy & Industrial
Strategy’s (BEIS) International Climate Finance. Preparatory
work started in March 2021 to support the retirement
and repurposing of four coal-fired power stations, totaling
about a 6 gigawatt (GW) capacity.
The report Coal Plant Repurposing for Ageing Coal Fleets in
Developing Countries was prepared, and published later,
in August 2021. The report presents a detailed cost-
benefit framework for examining the value proposition
of repurposing for three applications—solar energy
generation, battery energy storage, and synchronous
condenser (that produces fast reactive power essential
for maintaining system security)—and applies it to a
representative 1,000 megawatt (MW) coal plant in India,
finding a strong economic rationale for repurposing as part
of India’s just energy transition.
```

</details>

### A — 500 ký tự

Chunk ID: `a69d725ba4e4f6674936f3cf80ddfca13b037daac2c1ec6a1505db3f42c80f29`

```text
23
Foundations of Energy Transition
The outcomes achieved under the country grants were
complemented by the facility’s own knowledge work. In
December 2020, ESRF hosted its first virtual knowledge
forum for World Bank staff. The forum included a
comprehensive debate on the challenges of energy
subsidy reforms during and after the pandemic, as well
as knowledge exchange among diverse stakeholders,
including subject experts and government representatives.
SUPPORTING COAL REGIONS IN
TRANSITION
Coal
```

### B — 457 ký tự

Chunk ID: `31d04206460cc712852715ff0e58953e0af1450ac71712195945d0fbc6f51625`

```text
23
Foundations of Energy Transition
The outcomes achieved under the country grants were
complemented by the facility’s own knowledge work. In
December 2020, ESRF hosted its first virtual knowledge
forum for World Bank staff. The forum included a
comprehensive debate on the challenges of energy
subsidy reforms during and after the pandemic, as well
as knowledge exchange among diverse stakeholders,
including subject experts and government representatives.
```

**Bạn gửi vào chat:**
`Mẫu 08: A=..., B=..., C=...; lý do A: ...; lý do B/C: ...`

## Mẫu 09 — PDF 32 (trang in 24)

Section: Foundations of Energy Transition

Vị trí nguồn: ký tự 50, bắt đầu bằng **ESMAP has built**.

<details>
<summary>Xem toàn bộ văn bản trang nguồn để đối chiếu</summary>

```text
24
ESMAP Annual Report 2021
GENDER
FOCUS IN
ESMAP
ESMAP has built considerable momentum for closing gender gaps through
its global Gender and Energy program and its six regional gender programs.
These have helped strengthen women’s roles as consumers, employees, and
entrepreneurs in the energy sector. Aligned with the World Bank Group Gender
Strategy and lessons learned during its implementation, ESMAP works with
countries to design interventions and generate crucial knowledge of actions
needed to close gender gaps in the sector and improve development outcomes.
ESMAP gender activities address gender inequalities in the following areas:
• Improving female workforce participation in the energy sector
• Improving women’s productivity and livelihoods
• Improving women’s access to modern energy services that meet needs
Throughout FY2021, the Gender and Energy program continued to work closely with ESMAP’s other
programs to generate and disseminate knowledge on gender and energy and with the regional
Energy and Gender teams to address gender gaps in World Bank energy projects. The support
provided by regional Energy Gender Experts made a difference: in FY2021, 91 percent of all Energy
and Extractives Practice operations were gender-tagged, a substantial increase from 79 percent in
FY20. The Gender Tag identifies operations that seek to close gender gaps in human endowments,
more and better jobs, ownership and control of assets, and women’s voice and agency.
SIX REGIONAL GENDER AND ENERGY PROGRAMS
Each World Bank region hosts a gender program:
1. Africa Gender and Energy program
2. East Asia and Pacific Gender and Energy facility
3. Energy, Gender and Social Inclusion in the Europe and Central Asia region
4. Latin America and Caribbean Energy and Gender program
5. Middle East and North Africa Energy and Gender program
6. South Asia Gender and Energy Facility team
```

</details>

### A — 499 ký tự

Chunk ID: `f9b489a1cba8e5606ffa8b2772a4f6011033a958b10a7a231aef19270b0725c3`

```text
24
ESMAP Annual Report 2021
GENDER
FOCUS IN
ESMAP
ESMAP has built considerable momentum for closing gender gaps through
its global Gender and Energy program and its six regional gender programs.
These have helped strengthen women’s roles as consumers, employees, and
entrepreneurs in the energy sector. Aligned with the World Bank Group Gender
Strategy and lessons learned during its implementation, ESMAP works with
countries to design interventions and generate crucial knowledge of actions
needed
```

### B — 302 ký tự

Chunk ID: `9740cca72164b27a43bebcfd3bb0380b7256f62b5e532ae2f12ac2e5bc4750e4`

```text
24
ESMAP Annual Report 2021
GENDER
FOCUS IN
ESMAP
ESMAP has built considerable momentum for closing gender gaps through
its global Gender and Energy program and its six regional gender programs.
These have helped strengthen women’s roles as consumers, employees, and
entrepreneurs in the energy sector.
```

**Bạn gửi vào chat:**
`Mẫu 09: A=..., B=..., C=...; lý do A: ...; lý do B/C: ...`

## Mẫu 10 — PDF 33 (trang in 25)

Section: Foundations of Energy Transition

Vị trí nguồn: ký tự 77, bắt đầu bằng **In collaboration with the Gender team**.

<details>
<summary>Xem toàn bộ văn bản trang nguồn để đối chiếu</summary>

```text
25
Foundations of Energy Transition
GETTING TO GENDER
EQUALITY IN
HYDROPOWER
In collaboration with the Gender team,
ESMAP’s Hydropower Development Facility
is developing a gender and hydropower global
baseline and a report on women’s employment
in hydropower—including a survey launched
in the beginning of FY2022. This report will
provide tools and evidence for practitioners
to close employment gender gaps in the
hydropower sector.
WEST AFRICA: CAPACITY
BUILDING FOR WOMEN
ENTREPRENEURS IN
THE OFF-GRID SOLAR
SECTOR
In West Africa, ESMAP’s Off-Grid Solar Scale-Up
initiative is financing activities to close gender
gaps in accessing economic opportunity in the
off-grid solar sector. These activities are part
of the Regional Off-Grid Electricity Access project
and they include (1) engaging with women
entrepreneurs and providing them training
and capacity building support; (2) improving
women entrepreneurs’ access to credit; and (3)
increasing women’s awareness of employment
opportunities in the standalone solar systems
market.
ENERGY STORAGE
WOMEN’S MENTORSHIP
PROGRAM
The Energy Storage Program (ESP) fosters
gender equality in the energy storage sector
through its Women in Energy Storage (WES)
Mentoring Program in collaboration with
the Global Women’s Network for the Energy
Transition (GWNET). The mentoring program
focuses on career development and improving
technical knowledge on thermal energy storage
and battery storage for the grids, batteries
for renewable energy hybrids, and mini-grids.
In 2020, the program received over 240
applications from more than 50 countries. The
first cohort of the WES Mentoring Program
included 25 mid-career women from 17
countries, working in energy utilities, public
sector, private sector, consulting, and academia.
Following the success of the first edition, the ESP
and GWNET plan on opening applications for
the second cohort of mentees, thus continuing
to work together towards closing gender gaps in
the energy sector.
```

</details>

### A — 500 ký tự

Chunk ID: `6e2183726cc39c72982dca366d461380dc76dd14ecf50c2032e5f6a747f74db1`

```text
25
Foundations of Energy Transition
GETTING TO GENDER
EQUALITY IN
HYDROPOWER
In collaboration with the Gender team,
ESMAP’s Hydropower Development Facility
is developing a gender and hydropower global
baseline and a report on women’s employment
in hydropower—including a survey launched
in the beginning of FY2022. This report will
provide tools and evidence for practitioners
to close employment gender gaps in the
hydropower sector.
WEST AFRICA: CAPACITY
BUILDING FOR WOMEN
ENTREPRENEURS IN
THE OFF
```

### B — 434 ký tự

Chunk ID: `df278f7e626be44963091d46557d93f51dba2d4174a12f0e91c9c3512744f2f3`

```text
25
Foundations of Energy Transition
GETTING TO GENDER
EQUALITY IN
HYDROPOWER
In collaboration with the Gender team,
ESMAP’s Hydropower Development Facility
is developing a gender and hydropower global
baseline and a report on women’s employment
in hydropower—including a survey launched
in the beginning of FY2022. This report will
provide tools and evidence for practitioners
to close employment gender gaps in the
hydropower sector.
```

**Bạn gửi vào chat:**
`Mẫu 10: A=..., B=..., C=...; lý do A: ...; lý do B/C: ...`
