import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import {of} from "rxjs/index";


@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})

export class AppComponent {
  private title = 'app';
  private base_url: string = "http://localhost:8000";

  private specie_id: string = "9606";
  private amino_acid_sequence: string = "ATCDQYWEGLFHYKIRPHVVVPYQM";
  private primer_length: string = "12";
  private email: string = "shiv.prsd19@gmail.com";

  private specie_data = {};
  private result_data = {};
  private total_results = {};
  private page_offsets = [];
  private previous = "";
  private next = "";
  private start_count = "";
  private end_count = "";
  private least_degenerate_codon = "";

  private specie_data_loaded: boolean = false;
  private final_data_loaded: boolean = false;

  constructor(private http: HttpClient){}

  public fetchSpeciesData(){
      if(this.specie_id.trim() != ""){
          let url = this.base_url + "/api/load-species-data/?specie_id=" + this.specie_id;
          this.http.get(url).subscribe((res)=>{
            this.specie_data = res.species_data;
            this.specie_data_loaded = true;
          });
      }
  }

  public runApp(url){

      if(!Boolean(url)){
        url = this.base_url + "/api/run-app/?amino_acid_seq=" + this.amino_acid_sequence + "&email=" + this.email + "&primer_len=" + this.primer_length + "&specie_id="+this.specie_id;
      }

      this.http.get(url).subscribe((res)=>{
          this.final_data_loaded = true;
          this.result_data = res.results;
          this.page_offsets = [];
          if(Number(res.count) > 100){
              this.total_results = Number(res.count);
              this.previous = res.previous;
              this.next = res.next;
              this.least_degenerate_codon = res.results[0].aasldc;
              let first_page: boolean = true;
              let last_page: boolean = true;
              let limit = 100;
              let offset = 0;
              if(Boolean(this.previous)){
                first_page = false;
                let params = this.previous.split('?')[1].split('&');
                for(let i=0; i<params.length; i++){
                  let key=params[i].split('=')[0];
                  let value=params[i].split('=')[1];
                  if(key == 'offset') offset = Number(value);
                }
                offset += limit;
              }
              if(Boolean(this.next)){
                last_page = false;
                if(!Boolean(this.previous)){
                  let params = this.next.split('?')[1].split('&');
                  for(let i=0; i<params.length; i++){
                    let key=params[i].split('=')[0];
                    let value=params[i].split('=')[1];
                    if(key == 'offset') offset = Number(value);
                  }
                  offset -= limit;
                }
              }

              this.start_count = offset + 1;
              this.end_count = offset + limit;
              if(this.end_count > this.total_results) this.end_count = this.total_results;
              if(!first_page){
                if(Number((offset/limit)) > 1){
                  this.page_offsets.push({
                      url: this.base_url + "/api/run-app/?amino_acid_seq=" + this.amino_acid_sequence + "&email=" + this.email + "&primer_len=" + this.primer_length + "&specie_id="+this.specie_id + "&limit=" + limit + "&offset=0",
                      page_number: 1,
                      selected: false,
                  });
                }
                this.page_offsets.push({
                    url: this.base_url + "/api/run-app/?amino_acid_seq=" + this.amino_acid_sequence + "&email=" + this.email + "&primer_len=" + this.primer_length + "&specie_id="+this.specie_id + "&limit=" + limit + "&offset=" + (offset-limit),
                    page_number: Number(offset/limit),
                    selected: false,
                });
              }
              this.page_offsets.push({
                  url: this.base_url + "/api/run-app/?amino_acid_seq=" + this.amino_acid_sequence + "&email=" + this.email + "&primer_len=" + this.primer_length + "&specie_id="+this.specie_id + "&limit=" + limit + "&offset=" + (offset),
                  page_number: Number((offset/limit)+1),
                  selected: true,
              });
              if(!last_page){
                this.page_offsets.push({
                    url: this.base_url + "/api/run-app/?amino_acid_seq=" + this.amino_acid_sequence + "&email=" + this.email + "&primer_len=" + this.primer_length + "&specie_id="+this.specie_id + "&limit=" + limit + "&offset=" + (offset+limit),
                    page_number: Number((offset/limit)+2),
                    selected: false
                });
                let max_page:number = Number(this.total_results/limit);
                if(max_page.toFixed()*limit < this.total_results){
                  max_page = max_page.toFixed() + 1;
                }
                if(Number((offset/limit)) < max_page){
                  this.page_offsets.push({
                      "url": this.base_url + "/api/run-app/?amino_acid_seq=" + this.amino_acid_sequence + "&email=" + this.email + "&primer_len=" + this.primer_length + "&specie_id="+this.specie_id + "&limit=" + limit + "&offset=" + ((max_page.toFixed()*limit)-limit),
                      "page_number": max_page.toFixed(),
                      "selected": false,
                  });
                }
              }
          }
      });

  }

}
