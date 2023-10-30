from MyFPDFExtn_cpy import MyFPDF, BillTemplate
from modals import BillDataModel
from unused.services import BuildDataServices


def custStmt(stmtMsg):
    stmtMsg = stmtMsg.split('-')
    stmtMsg = [i.strip() for i in stmtMsg]
    custId = custId = 'CUST{0}'.format(stmtMsg[1].zfill(3))

    #----------------------COMPANY PROFILE---------------------------------------------------------------
    service = BuildDataServices(custId)
    modal = BillDataModel(service, '{0}-{1}'.format(stmtMsg[2], stmtMsg[3]))
    service._index = 0
    content = BillTemplate(modal)
    pdf = MyFPDF(content)

    content.document = content.DOCUMENT_TEMPLATE

    content.template = content.COMPANY_PROFILE_TEMPLATE
    pdf.writeRows()
    pdf.ln(10)

    print('Writing the statement for the duration {0}'.format(modal.get('**statement_period')))
    #---------------------STATEMENT OF ACCOUNT INFO------------------------------------------------------
    content.template = content.STMT_HEADER_TEMPLATE
    pdf.writeRows()
    pdf.ln(10)
    #--------------------CUSTOMER INFORMATION-------------------------------------------------------------
    content.template = content.CUST_INFO_HEAD_TEMPLATE
    pdf.writeRows()

    content.template = content.CUST_INFO_DATA_TEMPLATE
    pdf.writeRows()
    pdf.ln(10)

    #-------------------CUSTOMER OVER ALL STATEMENT REPORT (HEAD)------------------------------------------
    content.template = content.CUST_OVERALL_STMT_HEAD_TEMPLATE
    pdf.writeRows()

    while(modal.next()):
        print('\tPrinting data for {0}'.format(modal.get("**iteration_month")))

        #-------------------CUSTOMER OVER ALL STATEMENT REPORT (DATA)--------------------------------------
        pdf.ln(5)
        content.template = content.CUST_OVERALL_STMT_DATA1_TEMPLATE
        pdf.writeRows()

        content.template = content.CUST_OVERALL_STMT_DATA2_TEMPLATE
        pdf.writeRows()


    #-------------------CUSTOMER OVER ALL STATEMENT REPORT (RESULT)------------------------------------------
    content.template = content.CUST_OVERALL_STMT_RES_TEMPLATE
    pdf.writeRows()
    pdf.ln(20)

    modal.refresh()
    while modal.next():

        #----------------PURCHASE DETAILS INFO----------------------------------------------------------------
        # modal.set("purchase_month", '( '+month+' )')
        content.template = content.CUST_MONTH_STMT_TITLE_TEMPLATE
        pdf.writeRows()

        #----------------PURCHASE DETAILS (HEAD)----------------------------------------------------------------
        content.template = content.CUST_MONTH_STMT_HEAD_TEMPLATE
        pdf.writeRows()

        #----------------PURCHASE DETAILS (DATA)----------------------------------------------------------------
        content.template = content.CUST_MONTH_STMT_DATA1_TEMPLATE
        pdf.writeRows()

        content.template = content.CUST_MONTH_STMT_DATA2_TEMPLATE
        pdf.writeRows()
        pdf.ln(22)


    savePath = 'output/' + custId + '_' + stmtMsg[2].capitalize() + '_' + stmtMsg[3] + '_' + 'output' + '.pdf'
    pdf.save(savePath)
    return {"savePath": savePath, "custName": service.getCustName(), "stmtPeriod": modal.getStmtPeriod()}


if __name__ == '__main__':
    custStmt('bill-035-jul-23')
    