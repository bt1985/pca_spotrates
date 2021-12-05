library(ecb)
library(AzureStor)
bl <- storage_endpoint("", key="")
cont <- storage_container(bl, "ecbyc")
ecb_yield_curve_import <-function(start_date,end_date,yield_curve_old){

  ecb_import_start_date<-ymd(max(yield_curve_old$Date))
  if (ecb_import_start_date>=end_date){#subset existing yield curve
    mask <- (yield_curve_old$Date >= start_date) & (yield_curve_old$Date <= end_date)
    yield_curve <- yield_curve_old[mask,]
    return(yield_curve)
  } else {#download additional data
    ecb_import_start_date<-ecb_import_start_date+days(1)
    key <- "YC.B.U2.EUR.4F.G_N_C.SV_C_YM.SR_3M+SR_6M+SR_1Y+SR_2Y+SR_3Y+SR_4Y+SR_5Y+SR_6Y+SR_7Y+SR_8Y+SR_9Y+SR_10Y+SR_11Y+SR_12Y+SR_13Y+SR_14Y+SR_15Y+SR_16Y+SR_17Y+SR_18Y+SR_19Y+SR_20Y+SR_21Y+SR_22Y+SR_23Y+SR_24Y+SR_25Y+SR_26Y+SR_27Y+SR_28Y+SR_29Y+SR_30Y"
    filter <- list(startPeriod = as.character(ecb_import_start_date),endPeriod= as.character(end_date))
    ecb_spot_yield_long <- ecb::get_data(key, filter)
    if(nrow(ecb_spot_yield_long)>0){
      ecb_spot_yield_long$obstime <- convert_dates(ecb_spot_yield_long$obstime)
      ecb_spot_yield <- ecb_spot_yield_long %>% 
        select(-freq, -ref_area, -currency, -provider_fm, -instrument_fm, -provider_fm_id)%>%
        spread( key="data_type_fm", 
                value="obsvalue")%>% 
        rename(Date=obstime)%>%
        relocate(Date,SR_3M,SR_6M,SR_1Y,SR_2Y,SR_3Y,SR_4Y,SR_5Y,SR_6Y,SR_7Y,SR_8Y,SR_9Y,SR_10Y,SR_11Y,SR_12Y,SR_13Y,SR_14Y,SR_15Y,SR_16Y,SR_17Y,SR_18Y,SR_19Y,SR_20Y,SR_21Y,SR_22Y,SR_23Y,SR_24Y,SR_25Y,SR_26Y,SR_27Y,SR_28Y,SR_29Y,SR_30Y)
      
      yield_curve<-rbind(yield_curve_old,ecb_spot_yield)
      savetoazure(yield_curve) #save additional data to azure
    }else{
      yield_curve <- yield_curve_old
    }
    return(yield_curve)
  }
}


savetoazure<-function(yield_curve){
  storage_write_csv(yield_curve, cont, "ecb_spot_yield.csv")
}
