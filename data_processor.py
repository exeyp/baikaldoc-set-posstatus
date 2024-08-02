import logging

class DataProcessor:

    @staticmethod
    def process_and_build_mutation_queries(data, status_map):
        processed_data = []
        docrc_list = []
        # mutation_variables_list = []
        BATCH_SIZE = 20
        mutation_template = "mutation UpdateArRubricValues {{ {mutations} }}"
        mutation_queries = []

        for item in data:
            if item['posStatusRub'] is None:
                item['posStatusRub'] = status_map.get(item.get('eosSstuStatus'))
                docrc_list.append(item['refRubric']['docRc']['freeNum'])
                processed_data.append(item)
            
            # mutation_variables = {
            #         "input": {
            #             "data": {
            #                 "isnRefRubric": item['isnRefRubric'],
            #                 "posStatusRub": item['posStatusRub']
            #             }
            #         }
            #     }
            # mutation_variables_list.append(mutation_variables)

        for i in range(0, len(processed_data), BATCH_SIZE):
            batch = processed_data[i:i + BATCH_SIZE]
            mutations = []

            for idx, item in enumerate(batch):
                mutation_name = f"update{idx}"
                mutation = f"""
                {mutation_name}: updateArRubricValue(input: {{
                    clientMutationId: "{mutation_name}",
                    data: {{
                        isnRefRubric: {item['isnRefRubric']},
                        posStatusRub: "{item['posStatusRub']}"
                    }}
                }}) {{
                    success,
                    message
                    data {{
                        isnRefRubric,
                        posStatusRub
                    }}
                }}
                """
                mutations.append(mutation.strip())

            mutation_query = mutation_template.format(mutations=" ".join(mutations))
            mutation_queries.append(mutation_query)

        return mutation_queries, docrc_list
